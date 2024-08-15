import scrapy
import json
import re
from berghausScraping.utils import clean_text, barcode_type

class NikeSpider(scrapy.Spider):
    name = "nike_crawler"
    allowed_domains = ["nike.com"]
    start_urls = ["https://www.nike.com/"]
    seen_category_urls = set()
    seen_product_urls = set()
    seen_api_urls = set()

    def parse(self, response):
        try:
            category_urls = response.xpath('//header//a[@role="menuitem"]/@href').getall()
            for url in category_urls:
                if url not in self.seen_category_urls:
                    self.seen_category_urls.add(url)
                    yield response.follow(url, callback=self.parse_category)
        except Exception:
            print("Error occurred in parse function")

    def parse_category(self, response):
        try:
            conceptid = response.xpath("//meta[@name='branch:deeplink:$deeplink_path']/@content").get()
            conceptid = re.findall("conceptid=([\\w-]+(?:,[\\w-]+)*)", conceptid)
            conceptid = re.sub(r',', '%2C', conceptid[0]) if conceptid else None

            api_url = f'https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=C4E2BAEDB4E9F8B5CB49FE5588D01C43&country=us&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(US)%26filter%3Dlanguage(en)%26filter%3DemployeePrice(true)%26filter%3DattributeIds({conceptid})%26anchor%3D1%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%94%20%7BhighestPrice%7D'
            if api_url not in self.seen_api_urls:
                self.seen_api_urls.add(api_url)
                yield scrapy.Request(api_url, callback=self.parse_products, meta={'anchor': 1})
        except Exception:
            print("Error occurred in parse_category function")

    def parse_products(self, response):
        try:
            data = json.loads(response.text)
            products = data.get('data', {}).get('products', {}).get('products', [])

            for product in products:
                product_url = product.get('url', '').replace('{countryLang}', 'https://www.nike.com')
                if product_url not in self.seen_product_urls:
                    self.seen_product_urls.add(product_url)
                    yield response.follow(product_url, callback=self.product_description, meta={'product_url': product_url})

            next_page = data.get('data', {}).get('products', {}).get('pages', {}).get('next')
            if next_page:
                current_anchor = response.meta['anchor']
                next_anchor = current_anchor + 24
                next_url = response.url.replace(f'anchor%3D{current_anchor}', f'anchor%3D{next_anchor}')
                if next_url not in self.seen_api_urls:
                    self.seen_api_urls.add(next_url)
                    yield scrapy.Request(next_url, callback=self.parse_products, meta={'anchor': next_anchor})
        except Exception:
            print("Error occurred in parse_products function")

    def product_description(self, response):
        try:
            script_content = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
            if script_content:
                json_data = json.loads(script_content)
                products_data = json_data.get('props', {}).get('pageProps', {}).get('productGroups', {})[0]
                products = products_data.get('products', {})
                number_of_variations = json_data.get('props', {}).get('pageProps', {}).get('colorwayImages', {})
                if len(number_of_variations) > 1:
                    hasVariations = True
                else:
                    hasVariations = False

                for key, product in products.items():
                    product_info = product.get('productInfo')
                    product_sizes = product.get('sizes', [])
                    product_url = product_info.get('url')
                    product_title = product_info.get('fullTitle')
                    color = product.get('colorDescription')
                    brands = product.get('brands')
                    original_price = product.get('prices').get('initialPrice')
                    price = product.get('prices').get('currentPrice')
                    product_description = product_info.get('productDescription')
                    product_description = clean_text(product_description)
                    availability_status = product.get('statusModifier')
                    images = self.extract_image_urls(product)
                    image = images[0] if images else None

                    size_info = {}
                    for size in product_sizes:
                        label = size.get('localizedLabel')
                        merch_sku_id = size.get('merchSkuId')
                        barcode = size.get('gtins')[0].get('gtin')
                        if label and merch_sku_id:
                            size_info[label] = {
                                'merch_sku_id': merch_sku_id,
                                'barcode': barcode
                            }

                    if availability_status != 'OUT_OF_STOCK':
                        merch_product_id = product.get('merchProductId', None)
                        sizes_api = f"https://api.nike.com/cic/grand/v1/graphql/getfulfillmentofferings/v5?variables=%7B%22countryCode%22%3A%22US%22%2C%22currency%22%3A%22USD%22%2C%22locale%22%3A%22en-US%22%2C%22locationId%22%3A%22%22%2C%22locationType%22%3A%22STORE_VIEWS%22%2C%22offeringTypes%22%3A%5B%22SHIP%22%5D%2C%22postalCode%22%3A%22%22%2C%22productId%22%3A%22{merch_product_id}%22%7D"
                        meta_data = {
                            'size_info': size_info,
                            'product_url': product_url,
                            'product_title': product_title,
                            'variation': hasVariations,
                            'color': color,
                            'brands': brands,
                            'price': price,
                            'product_description': product_description,
                            'image': image,
                            'images': images,
                        }
                        yield scrapy.Request(url=sizes_api, callback=self.parse_sizes, meta=meta_data)

                    else:
                        yield {
                            'url': product_url,
                            'title': product_title,
                            'variation': hasVariations,
                            'color': color,
                            'brands': brands,
                            'price': price,
                            "isPriceExcVAT": False,
                            'product_description': product_description,
                            'image': image,
                            'images': images,
                            'status': 'NO SIZE AVAILABLE',
                            'availability': False,
                        }
        except Exception:
            print("Error occurred in product_description function")

    def parse_sizes(self, response):
        try:
            data_json = json.loads(response.text)
            api_sizes = data_json.get('data', {}).get('fulfillmentOfferings', {}).get('items', [])
            size_info = response.meta.get('size_info', {})
            api_size_sku_set = set()
            for size in api_sizes:
                sku_id = size.get('skuId')
                if sku_id:
                    api_size_sku_set.add(sku_id)
            api_size_sku_list = list(api_size_sku_set)
            if len(api_size_sku_list) > 1 and response.meta.get('variation') == True:
                hasVariations = True
            else:
                hasVariations = False

            matched_sizes = {}
            unmatched_sizes = {}

            for label, info in size_info.items():
                merch_sku_id = info['merch_sku_id']
                barcode = info['barcode']
                barcodeType = barcode_type(barcode)
                if merch_sku_id in api_size_sku_list:
                    item = {
                        'url': f"{response.meta.get('product_url')}?ah={merch_sku_id}",
                        'title': response.meta.get('product_title'),
                        'variation': hasVariations,
                        'color': response.meta.get('color'),
                        'brands': response.meta.get('brands'),
                        'price': response.meta.get('price'),
                        "isPriceExcVAT": False,
                        'product_description': response.meta.get('product_description'),
                        'image': response.meta.get('image'),
                        'images': response.meta.get('images'),
                        'size': label,
                        'sku': merch_sku_id,
                        'barcode': barcode,
                        'barcode_type': barcodeType,
                        'availability': True,
                    }
                    yield item
                    matched_sizes[merch_sku_id] = True
                else:
                    unmatched_sizes[merch_sku_id] = {
                        'url': f"{response.meta.get('product_url')}?ah={merch_sku_id}",
                        'title': response.meta.get('product_title'),
                        'variation': hasVariations,
                        'color': response.meta.get('color'),
                        'brands': response.meta.get('brands'),
                        'price': response.meta.get('price'),
                        "isPriceExcVAT": False,
                        'product_description': response.meta.get('product_description'),
                        'image': response.meta.get('image'),
                        'images': response.meta.get('images'),
                        'size': label,
                        'sku': merch_sku_id,
                        'barcode': barcode,
                        'barcode_type': barcodeType,
                        'availability': False,
                    }

            for item in unmatched_sizes.values():
                yield item
        except Exception:
            print("Error occurred in parse_sizes function")

    def extract_image_urls(self, json_data):
        try:
            images = json_data.get('contentImages', [])
            filtered_urls = []

            for image in images:
                if image.get('cardType') == 'image':
                    properties = image.get('properties', {})
                    squarish = properties.get('squarish', {})
                    if squarish.get('aspectRatio') == 1:
                        url = squarish.get('url')
                        if url:
                            filtered_urls.append(url)

            return filtered_urls
        except Exception:
            print("Error occurred in extract_image_urls function")

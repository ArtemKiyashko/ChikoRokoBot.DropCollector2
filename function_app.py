import azure.functions as func
import cloudscraper
import logging
import os
from azure.identity import DefaultAzureCredential
from azure.storage.queue import TextBase64EncodePolicy, QueueClient
from lxml import html

app = func.FunctionApp()

@app.function_name(name="DropCollectorAntiBot")
@app.schedule(schedule="0 */5 * * * *", 
              arg_name="mytimer",
              run_on_startup=True) 
def main(mytimer: func.TimerRequest) -> None:
    DropCollectorOptions__Url = os.environ.get('DropCollectorOptions__Url', 'https://chikoroko.art/en')
    DropCollectorOptions__DataElementQuerySelector = os.environ.get('DropCollectorOptions__DataElementQuerySelector', '//script[@id="__NEXT_DATA__"]')
    DropCollectorOptions__StorageAccount = os.environ.get('DropCollectorOptions__StorageAccount', 'UseDevelopmentStorage=true')
    DropCollectorOptions__QueueName = os.environ.get('DropCollectorOptions__QueueName', 'alldrops')

    scraper = cloudscraper.create_scraper()
    response = scraper.get(DropCollectorOptions__Url)
    tree = html.fromstring(response.text)
    rawDataObject = tree.xpath(DropCollectorOptions__DataElementQuerySelector)[0]

    queue_client = QueueClient(
        DropCollectorOptions__StorageAccount, 
        queue_name=DropCollectorOptions__QueueName, 
        credential=DefaultAzureCredential(),
        message_encode_policy = TextBase64EncodePolicy())
    
    queue_client.send_message(rawDataObject.text)
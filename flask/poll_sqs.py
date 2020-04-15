import boto3
import time
import json
import requests

# ./kinesis_video_gstreamer_sample_app ARCRecognitionPrototypeStream
# aws rekognition start-stream-processor --name streamProcessorForBlog --region us-west-2
# aws rekognition list-stream-processors --region us-west-2
# aws rekognition index-faces --image '{"S3Object":{"Bucket":"arc-facial-rec","Name":"<MYFACE_KEY>.jpeg"}}' --collection-id "arc-face-rec-test" --detection-attributes "ALL" --external-image-id "<YOURNAME>" --region us-west-2
# ./webcam_to_kinesis ARCRecognitionPrototypeStream

def poll():
    client = boto3.client('sqs')
    client.create_queue(QueueName='facial_recognition')

    queues = client.list_queues(QueueNamePrefix='facial_recognition')
    face_rec_queue = queues['QueueUrls'][0]

    server_url = "http://127.0.0.1:5000/person"

    while True:
        messages = client.receive_message(QueueUrl=face_rec_queue,MaxNumberOfMessages=1,WaitTimeSeconds=20)
        if 'Messages' in messages:
            for message in messages['Messages']:
                try:
                    recognition_result = json.loads(message['Body'])
                    output = ''
                    for result in recognition_result:
                        for person in result:
                            # print(person)
                            if person and person['Face']:
                                output += 'Name: ' + person['Face']['ExternalImageId'] + ', Confidence: ' + str(person['Face']['Confidence']) + ', Similarity: ' + str(person['Similarity']) + '<br>'
                            
                    print(output)
                    requests.post(server_url, data=output)
                    print()
                    client.delete_message(QueueUrl=face_rec_queue,ReceiptHandle=message['ReceiptHandle'])
                except Exception as e:
                    print('Exception: ' + str(e.with_traceback))

if __name__ == '__main__':
    poll()
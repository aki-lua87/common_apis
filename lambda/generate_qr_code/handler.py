import qrcode
import base64


def main(event, context):
    # クエリ文字列から
    qr_code_content = event.get('queryStringParameters', {'content': ''}).get('content', '')
    # でけえのは嫌なので1000文字を越えるならエラー
    if len(qr_code_content) > 1000 or len(qr_code_content) == 0:
        return {
            'statusCode': 400,
            'body': 'QRコードの内容は0文字以上1000文字以内で指定してください'
        }
    # QRコードを生成
    img = qrcode.make(qr_code_content)
    img.save("/tmp/qrcode.png")
    with open("/tmp/qrcode.png", "rb") as f:
        bytes_image = f.read()
        encoded_image = base64.b64encode(bytes_image).decode("utf-8")
        print(encoded_image)
        # 生成したQRコードをレスポンスとして返す
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'image/png'
            },
            "isBase64Encoded": True,
            # バイナリデータをBase64エンコードして返す
            'body': encoded_image
        }

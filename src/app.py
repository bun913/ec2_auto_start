import boto3
from botocore.exceptions import ClientError
import json


class ResponseHandler:
    ERR_TEMPLATE = {
        "errorType": "",
        "errorMessage": ""
    }
    RES_TEMPLATE = {
        "Message": ""
    }

    def __init__(self):
        self.errors = []

    def append_eroor(self, type: str, message: str):
        """返却するエラー内容をセット

        Args:
            type str: エラータイプ
            message str: エラーメッセージ
        """
        dic = ResponseHandler.ERR_TEMPLATE.copy()
        dic['errorType'] = type
        dic['errorMessage'] = message
        self.errors.append(dic)

    def return_errors(self) -> str:
        """エラーメッセージの返却

        Returns:
            str: JSON形式のエラー内容
        """
        raise Exception(json.dumps(self.errors))

    def get_respose(self, body: str) -> str:
        """
        レスポンスをJsonで返却
        通常成功時はEC2インスタンスのidをリスト形式で返却

        Args:
            body str: レスポンス内容
        """
        dic = ResponseHandler.RES_TEMPLATE.copy()
        dic['Message'] = body
        return json.dumps(dic)


response = ResponseHandler()


def lambda_handler(event, context):
    instances = get_ec2_instances()
    try:
        
        instances.start()
    except ClientError as e:
        response.append_eroor(type="ClientError", message=str(e))
        response.return_errors()
    except Exception as e:
        response.append_eroor(type="UnExpectedError", message=str(e))
        response.return_errors()
    id_list = [instance.id for instance in instances]
    return response.get_respose(",".join(id_list))


def get_ec2_instances():
    """EC2インスタンスを取得
    """
    ec2 = boto3.resource('ec2')
    filter = [
        {
            'Name': 'tag:Reboot',
            'Values': ['True']
        },
        {
            'Name': 'instance-state-name',
            'Values': ['stopped']
        }
    ]
    result = ec2.instances.filter(Filters=filter)
    return result

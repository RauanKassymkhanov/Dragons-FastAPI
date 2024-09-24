from polyfactory.factories.pydantic_factory import ModelFactory
from aws_lambda_powertools.utilities.parser.models.dynamodb import (
    DynamoDBStreamChangedRecordModel,
    DynamoDBStreamRecordModel,
)
from aws_lambda_powertools.utilities.parser.models.sqs import SqsRecordModel, SqsAttributesModel
from app.daily_reporter.schemas import DailyReportModel


class DynamoDBStreamChangedRecordFactory(ModelFactory[DynamoDBStreamChangedRecordModel]):
    __model__ = DynamoDBStreamChangedRecordModel

    @classmethod
    def NewImage(cls):
        return None

    @classmethod
    def OldImage(cls):
        return None


class DynamoDBStreamRecordFactory(ModelFactory[DynamoDBStreamRecordModel]):
    __model__ = DynamoDBStreamRecordModel

    @classmethod
    def dynamodb(cls) -> DynamoDBStreamChangedRecordModel:
        return DynamoDBStreamChangedRecordFactory.build()

    @classmethod
    def eventName(cls) -> str:
        return "INSERT"


class SqsAttributesModelFactory(ModelFactory[SqsAttributesModel]):
    __model__ = SqsAttributesModel


class SqsRecordModelFactory(ModelFactory[SqsRecordModel]):
    __model__ = SqsRecordModel

    @classmethod
    def attributes(cls) -> SqsAttributesModel:
        return SqsAttributesModelFactory.build()

    @classmethod
    def body(cls) -> DynamoDBStreamRecordModel:
        return DynamoDBStreamRecordFactory.build()


class DailyReportModelFactory(ModelFactory[DailyReportModel]):
    __model__ = DailyReportModel

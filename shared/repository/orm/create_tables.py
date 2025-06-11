# import os
# from dotenv import load_dotenv
#
# from sqlalchemy import create_engine
#
# from repository.orm.base import Base
#
# load_dotenv()
#
# db_url = "postgresql://" + os.environ["AWS_RDS_USERNAME"] + ":" + os.environ["AWS_RDS_PASSWORD"] + \
#          "@" + os.environ['AWS_RDS_ENDPOINT'] + ":" + os.environ['AWS_RDS_PORT'] + "/" + \
#          os.environ['AWS_RDS_DB_NAME']
#
# print(f"Will create engine for URL: {db_url}")
# db_engine = create_engine(db_url)
# print(f"Created engine")
#
# def create_tables():
#     print(f"Will create tables")
#     Base.metadata.create_all(db_engine)
#     print("Tables created")
#
# create_tables()
# # with db_engine.connect() as connection:
# #     print("Connected")
from amazon_s3.amazon_s3 import AmazonS3

from google_drive.google_drive import Google_Drive



# gd = Google_Drive("credentials.json", "google_types.data")
# gd.delete_all_files()
# gd.show_full_stats()
# gd.upload_local("/home/mih011/Desktop/Transfer")
# gd.show_full_stats()
# gd.download_local("/home/mih011/Desktop/Transfer_test")

s3 = AmazonS3("epic-shelter",12)
# s3.upload_local("/home/mih011/Desktop/Transfer")
# s3.download_local("/home/mih011/Desktop/Transfer_test")
s3.delete_all_files()

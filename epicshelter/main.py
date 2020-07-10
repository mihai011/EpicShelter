from amazon_s3.amazon_s3 import AmazonS3

from google_drive.google_drive import Google_Drive

from shelter.shelter import Shelter


gd = Google_Drive("credentials.json")
gd.delete_all_files()
# gd.test_method()
# # gd.show_full_stats()
#gd.upload_local("/home/mih011/Desktop/TestFinal")
# # gd.show_full_stats()
#gd.download_local("/home/mih011/Desktop/Transfer_test")

s3 = AmazonS3("epic-shelter",12)
#s3.delete_all_files()
#s3.upload_local("/home/mih011/Desktop/Transfer")
# s3.upload_local("/home/mih011/Desktop/Transfer_test")
# s3.delete_all_files()

# # #gd = Google_Drive("credentials.json", "google_types.data")
# # s3 = AmazonS3("epic-shelter",12)
#s3.get_all_file_ids_paths()
#gd.get_all_file_ids_paths()

sh = Shelter(1)

sh.register("google",gd)
sh.register("s3",s3)

sh.transfer("s3","google")
#s3.delete_all_files()
#s3.download_local("/home/mih011/Desktop/Transfer_test")
#gd.delete_all_files()

from SecureData import SecureData

sec_data = SecureData("smit", "RrzOVscYEKMp7MAh9NmL5hfQiB03")
print(sec_data.encrypt("Hello"))
print(sec_data.key)
print(sec_data.decrypt(sec_data.encrypt("Hello")))

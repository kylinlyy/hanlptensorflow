import os
import data_reader
def get_all_file_name(file_dir):
    count=0
    for root, dirs, files in os.walk(file_dir):
        for file_name in files:
            file_name="data\\requirement_example\\"+file_name
            print("file_name:",file_name)
            fulltext = data_reader.input_pdf(file_name)
            if data_reader.find_catalogue(fulltext)!=None:
                count+=1
    return count
print(get_all_file_name("data\\requirement_example"))

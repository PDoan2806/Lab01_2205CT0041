import numpy as np
import os
#TODO: Import lớp hệ thống hoặc các hàm lõi từ mã nguồn
import sys
from acquisition import FingerprintAcquisition
from features import FeatureExtractor
from preprocessing import PreprocessingPipeline
Absolute_Path=os.path.dirname(os.path.abspath(__file__))
if Absolute_Path not in sys.path:
    sys.path.insert(0, Absolute_Path)

def extract_and_export():

    #TODO: Khởi tạo đối tượng hệ thống

    raw_dir = os.path.join(os.path.dirname(__file__), '../raw_data')
    export_dir = os.path.join(os.path.dirname(__file__), '../exported_data')

    if not os.path.exists(export_dir): 
        print(f"File not found: {export_dir}")
        os.makedirs(export_dir)
        print(f"Folder created: {export_dir}")
    if not os.path.exists(raw_dir):
        print(f"File not found: {raw_dir}")
        os.makedirs(raw_dir)
        print(f"Folder created: {raw_dir}")

    acquisition = FingerprintAcquisition() 
    preprocessor = PreprocessingPipeline()    
    extractor = FeatureExtractor()
    for filename in os.listdir(raw_dir):

        if filename.endswith(('.png', '.tif')):

            img_path = os.path.join(raw_dir, filename)

            

            #TODO: Gọi hàm xử lý ảnh vân tay từ hệ thống để lấy danh sách minutiae
            raw_image = acquisition.load_fingerprint(img_path)

            results = preprocessor.preprocess(raw_image)

            minutiae_list, _ = extractor.extract_all(
                results['skeleton'],
                results['orientation']
            )            
            if minutiae_list:

                #TODO: Lọc và trích xuất tọa độ X, Y, Theta từ danh sách trả về
                data = np.array([
                    [minutia.x / denominator_x,
                    minutia.y / denominator_y,
                    minutia.orientation]
                    for minutia in minutiae_list
                ], dtype=np.float32)

                

                #TODO: Chuẩn hóa tọa độ X, Y về khoảng [0, 1]
                height, width = raw_image.shape[:2]
                denominator_x = max(width - 1, 1)
                denominator_y = max(height - 1, 1)
                
                out_path = os.path.join(export_dir, filename.replace('.tif', '.npy').replace('.png', '.npy'))

                np.save(out_path, data)

                print(f"Xử lý thành công: {filename}")

if __name__ == "__main__":

    extract_and_export()

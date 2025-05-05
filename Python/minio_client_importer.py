import os
import time
from minio import Minio
from minio.error import S3Error

# Cấu hình MinIO client
def get_minio_client():
    minio_endpoint = os.environ.get('MINIO_ENDPOINT', 'localhost:9000')
    minio_access_key = os.environ.get('MINIO_ROOT_USER')
    minio_secret_key = os.environ.get('MINIO_ROOT_PASSWORD')
    secure = os.environ.get('MINIO_SECURE', 'false').lower() == 'true'

    print(f"✅ Kết nối đến MinIO tại {minio_endpoint}")
    print(f"✅ MINIO_ROOT_USER={minio_access_key}")

    client = Minio(
        minio_endpoint,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=secure
    )
    return client

def ensure_bucket_exists(client, bucket_name):
    try:
        if not client.bucket_exists(bucket_name):
            print(f"Tạo bucket {bucket_name}...")
            client.make_bucket(bucket_name)
            # Thiết lập policy cho bucket để cho phép tải xuống
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                    }
                ]
            }
            # Chuyển đổi policy thành JSON string
            client.set_bucket_policy(bucket_name, str(policy))
            print(f"✅ Đã tạo bucket {bucket_name} và thiết lập quyền download")
        else:
            print(f"✅ Bucket {bucket_name} đã tồn tại")
    except S3Error as e:
        print(f"❌ Lỗi khi tạo bucket: {e}")

def upload_files_to_minio(client, local_folder, bucket_name):
    # Kiểm tra thư mục local có tồn tại không
    if not os.path.exists(local_folder):
        print(f"❌ Thư mục {local_folder} không tồn tại")
        return

    # In số lượng file trong thư mục
    total_files = sum(len(files) for _, _, files in os.walk(local_folder))
    print(f"📂 Tổng số file trong thư mục {local_folder}: {total_files}")
    # Lấy danh sách tất cả các file trong thư mục
    for root, _, files in os.walk(local_folder):
        for file in files:
            local_file_path = os.path.join(root, file)

            # Tính toán object name (đường dẫn trong bucket)
            # Nếu muốn giữ cấu trúc thư mục, sử dụng đoạn code này:
            # rel_path = os.path.relpath(local_file_path, local_folder)
            # object_name = rel_path.replace("\\", "/")

            # Nếu chỉ muốn lưu tên file (không giữ cấu trúc thư mục):
            object_name = os.path.basename(local_file_path)

            try:
                # Kiểm tra xem file đã tồn tại trong bucket chưa
                try:
                    client.stat_object(bucket_name, object_name)
                    print(f"⏭️ File đã tồn tại trong bucket: {object_name}")
                except S3Error:
                    # File chưa tồn tại, upload lên
                    print(f"📤 Uploading: {object_name}")
                    client.fput_object(
                        bucket_name,
                        object_name,
                        local_file_path,
                        # Tự động xác định content-type dựa trên phần mở rộng của file
                        content_type='application/octet-stream'
                    )
                    print(f"✅ Đã upload: {object_name}")

            except S3Error as e:
                print(f"❌ Lỗi khi upload {object_name}: {e}")

def main():
    bucket_name = "uavpov1"
    local_folder = "/init-images"

    # Đợi MinIO sẵn sàng
    retry_count = 0
    max_retries = 30
    retry_interval = 5  # seconds

    print("Đợi MinIO sẵn sàng...")

    while retry_count < max_retries:
        try:
            client = get_minio_client()
            # Kiểm tra kết nối bằng cách list buckets
            client.list_buckets()
            print("✅ Đã kết nối thành công đến MinIO")
            break
        except Exception as e:
            print(f"...MinIO chưa sẵn sàng, đợi thêm... ({e})")
            retry_count += 1
            time.sleep(retry_interval)

    if retry_count >= max_retries:
        print("❌ Không thể kết nối đến MinIO sau nhiều lần thử")
        return

    # Đảm bảo bucket tồn tại
    ensure_bucket_exists(client, bucket_name)

    # Upload tất cả file từ thư mục local
    upload_files_to_minio(client, local_folder, bucket_name)

    print(f"✅ Đã hoàn thành việc import ảnh từ {local_folder} vào bucket {bucket_name}")

if __name__ == "__main__":
    main()
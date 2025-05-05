#!/bin/sh
echo "✅ MINIO_ROOT_USER=$MINIO_ROOT_USER"
echo "✅ MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD"

echo "Đợi MinIO sẵn sàng..."
echo "Login vào MinIO với tài khoản ${MINIO_ROOT_USER} và mật khẩu ${MINIO_ROOT_PASSWORD}"
until /usr/bin/mc alias set minio http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}; do
    echo "...MinIO chưa sẵn sàng, đợi thêm..." && sleep 5;
done

# Tạo bucket nếu chưa có
if ! /usr/bin/mc ls minio/uavpov1 >/dev/null 2>&1; then
    echo "Tạo bucket uavpov1..."
    /usr/bin/mc mb minio/uavpov1
    /usr/bin/mc anonymous set download minio/uavpov1
fi


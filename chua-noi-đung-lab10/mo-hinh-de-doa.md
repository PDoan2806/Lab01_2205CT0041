# Mô hình đe doạ của hệ thống xác thực khuôn mặt, nhóm {số nhóm}

Học phần 04211 Bảo mật sinh trắc, bài TH10. Khung tám điểm tấn công theo Ratha, Connell và Bolle (2001), IBM Systems Journal 40(3); xem thêm Jain và cộng sự (2024), Chương 9, tr. 343-397.

## 1. Tài sản cần bảo vệ và giả định

| Tài sản | Vì sao quan trọng | Nơi lưu trong hệ thống của nhóm |
|---|---|---|
| Ảnh khuôn mặt khi thu nhận | dữ liệu sinh trắc học, dữ liệu cá nhân nhạy cảm | Chỉ nằm trong bộ nhớ khi chương trình chạy (`sample["image"]`), không ghi ra đĩa. Ảnh LFW nằm ở thư mục `lfw_funneled` trên máy và được xoá cuối buổi |
| Mẫu sinh trắc đã bảo vệ (BioHash) | nếu lộ cùng token thì bị so khớp được | Tệp JSON trong `ket-qua/` (chuỗi 128 bit mỗi người, kèm HMAC), do `TemplateStore.put` ghi |
| Token của người dùng | yếu tố sở hữu, khoá mở tính thu hồi | Trên thiết bị của người dùng, không lưu trong kho mẫu. Trong chương trình đánh giá là biến `tokens` trong bộ nhớ |
| Khoá HMAC của kho mẫu | chống sửa đổi mẫu | Biến môi trường `TH10_STORE_KEY`, không ghi vào mã nguồn hay Git |
| Nhật ký kiểm toán | truy vết sự cố | Tệp `.jsonl` trong `ket-qua/`, mỗi sự kiện một dòng, do `AuditLog.write` chỉ ghi thêm; không chứa ảnh, embedding hay mẫu |

Giả định về kẻ tấn công: có ảnh công khai của nạn nhân (in ra hoặc phát lại trên màn hình), có token của nạn nhân (kịch bản xấu mà nhóm dùng để chọn ngưỡng so khớp), nhưng không có quyền ghi vào máy chủ hay mã nguồn và không có khoá HMAC. Riêng các điểm 3, 5 và 8 ở bảng dưới, nhóm xét thêm trường hợp kẻ tấn công có quyền sửa mã chạy trên máy, vì đó là lúc các điểm này mới bị tấn công được. {nhóm xác nhận lại giả định này}

## 2. Bảng tám điểm tấn công

| Điểm | Mô tả | Ví dụ cụ thể với hệ thống của nhóm | Biện pháp đã cài đặt (tên hàm) | Biện pháp còn thiếu | Rủi ro còn lại (thấp, trung bình, cao) và lý do |
|---|---|---|---|---|---|
| 1 | Trình diện đặc điểm giả tại cảm biến | ảnh in, màn hình phát lại, mặt nạ | `DeepFacePad.score` chấm điểm ảnh; `AuthSystem.verify` từ chối khi điểm dưới `pad_threshold` | Mới thử ảnh in và phát lại (mô phỏng); chưa có dữ liệu mặt nạ hay video do AI tạo; ngưỡng PAD chưa chọn theo APCER mục tiêu | Cao nếu APCER phát lại còn cao: ở TH08 là 77,78% với ngưỡng 0,5 (dữ liệu mô phỏng). {cập nhật theo APCER đo ở TH10} |
| 2 | Gửi lại hoặc chèn tín hiệu đã số hoá, vượt qua cảm biến | video quay sẵn, camera ảo, mã độc thay khung hình | Chưa có | Ký khung hình ngay tại camera hoặc vùng bảo mật của thiết bị; kiểm tra toàn vẹn thiết bị và ứng dụng (phát hiện camera ảo, máy root); thách thức - phản hồi của TH08 chưa ghép vào luồng | Cao: PAD ở tầng ảnh không phân biệt được khung hình chèn vào. Ở TH08, video quay sẵn vượt thách thức trái/phải 25% (2/8) |
| 3 | Thay thế hoặc can thiệp bộ trích đặc trưng | sửa mã để trả embedding cố định | Chưa có (`DeepFaceEmbedder.embed` chạy cùng tiến trình, mã không được ký) | Ghim phiên bản thư viện và mô hình, kiểm tra mã băm trọng số, chạy bộ trích đặc trưng trong môi trường tin cậy | Trung bình: kẻ tấn công cần quyền sửa mã hoặc thư viện trên máy chạy |
| 4 | Sửa đổi vector đặc trưng trên đường truyền | chặn và thay embedding giữa hai mô-đun | Embedding đi thẳng từ `embed` sang `BioHashProtector.protect` trong cùng tiến trình và không lưu lại | Nếu sau này tách thành dịch vụ riêng thì cần TLS và xác thực hai đầu | Thấp trong thiết kế một tiến trình; sẽ tăng nếu tách dịch vụ |
| 5 | Thay thế bộ so khớp để luôn trả điểm cao | sửa hàm similarity | Chưa có (`BioHashProtector.similarity` không được bảo vệ) | Kiểm tra toàn vẹn mã, chạy so khớp ở bên tin cậy, kiểm thử tự động bằng các cặp mẫu đã biết kết quả | Trung bình đến cao: một dòng sửa là đủ nếu có quyền ghi mã |
| 6 | Sửa đổi, đánh cắp mẫu trong cơ sở dữ liệu | thay mẫu của nạn nhân bằng mẫu của kẻ tấn công | `TemplateStore.put` ký HMAC-SHA256, `TemplateStore.get` kiểm bằng `hmac.compare_digest`; kho chỉ chứa BioHash, không có ảnh hay embedding; token không nằm trong kho | Mã còn khoá mặc định `khoa-chi-dung-khi-thu-nghiem` khi chưa đặt `TH10_STORE_KEY`; HMAC không chống được việc đưa lại một kho cũ còn hợp lệ (rollback) | Thấp đến trung bình nếu khoá được giữ kín; cao nếu dùng khoá mặc định |
| 7 | Tấn công kênh giữa cơ sở dữ liệu và bộ so khớp | thay mẫu khi đang truyền | `TemplateStore.get` kiểm HMAC mỗi lần đọc nên mẫu bị thay giữa đường sẽ bị từ chối | Chưa có số phiên bản hay thời gian trong phần được ký, nên vẫn bị phát lại kho cũ; cần TLS nếu tách dịch vụ | Thấp |
| 8 | Ghi đè quyết định cuối cùng | sửa kết quả chấp nhận hoặc từ chối | `DecisionPolicy` và `AuthSystem.verify` quyết định; `AuditLog.write` ghi mọi quyết định | Nhật ký chưa được ký và chưa chống xoá; quyết định nằm cùng nơi với mã có thể bị sửa, chưa tách sang máy chủ và chưa có chữ ký kết quả | Cao nếu kẻ tấn công chạy được mã: sửa `verify` trả về đúng là xong, và nhật ký có thể bị xoá |

## 3. Ba mối đe doạ ưu tiên

**Điểm 2: chèn khung hình vào chuỗi xử lý.** Kẻ tấn công cài mã độc hoặc camera ảo trên điện thoại nạn nhân, rồi đưa vào chuỗi xử lý một video đã quay sẵn khuôn mặt nạn nhân (hoặc một khuôn mặt tạo bằng AI), có làm theo vài yêu cầu trái/phải. PAD không thấy gì lạ vì đã nhận khung hình đã qua cảm biến, và phần so khớp thấy một khuôn mặt đúng người. Người dùng thật có thể bị mất tiền hoặc tài khoản mà không hay biết. Biện pháp đề xuất: ký khung hình ở camera hoặc vùng bảo mật của thiết bị, kiểm tra toàn vẹn thiết bị, và thêm thách thức - phản hồi ngẫu nhiên từ TH08 vào trước PAD. Cách đo: với 5 bước ngẫu nhiên thì đoán mò đúng xác suất (1/2)⁵ ≈ 3%; chạy ít nhất 100 lượt video quay sẵn, chỉ số là tỷ lệ vượt thách thức (kỳ vọng gần 3%), và tỷ lệ chấp nhận của khung hình không ký (phải là 0%).

**Điểm 1: ảnh phát lại qua được PAD.** Kẻ tấn công lấy ảnh công khai của nạn nhân, phát lên màn hình điện thoại trước camera, và dùng token của nạn nhân (kịch bản xấu). Nếu APCER của loài này còn cao thì chỉ còn bước so khớp và khoá tài khoản chặn lại. Tác động: người dùng bị mạo danh dù không lộ gì ngoài ảnh mặt đã đăng công khai. Biện pháp đề xuất: nâng ngưỡng PAD, thu và đo bằng ảnh phát lại thật, bổ sung các loài tấn công còn thiếu (mặt nạ, video do AI tạo). Cách đo: APCER của từng loài với ít nhất 100 lần tấn công mỗi loài (nếu không lần nào lọt thì cận trên 95% xấp xỉ 3%); mục tiêu APCER lớn nhất không quá 5%, và IAPAR toàn luồng dưới 7%.

**Điểm 8: sửa quyết định cuối cùng.** Kẻ tấn công có quyền ghi mã trên máy chạy hệ thống, sửa `AuthSystem.verify` để luôn trả `True`, rồi xoá dòng tương ứng trong nhật ký. Các biện pháp PAD, so khớp và khoá tài khoản đều vô tác dụng, và hệ thống không còn dấu vết. Tác động: mọi tài khoản có thể bị mở. Biện pháp đề xuất: đưa quyết định sang máy chủ riêng, mã hoá kênh, ký kết quả quyết định, và ký nhật ký theo chuỗi băm để nhận ra dòng bị xoá. Cách đo: viết kiểm thử tự động sửa kết quả hoặc xoá một dòng nhật ký, chạy ít nhất 20 lần, và chỉ số là tỷ lệ lần hệ thống phát hiện (phải là 100%).

## 4. Đối chiếu yêu cầu

| Yêu cầu | Nguồn | Hệ thống của nhóm đáp ứng? | Bằng chứng |
|---|---|---|---|
| Sinh trắc học chỉ dùng trong xác thực đa yếu tố cùng thiết bị xác thực vật lý | NIST SP 800-63B-4, mục 3.2.3 | Một phần | `BioHashProtector.protect(emb, token)` cần cả khuôn mặt lẫn token nên là hai yếu tố; nhưng token hiện chỉ là một chuỗi trong chương trình, chưa gắn với thiết bị xác thực vật lý |
| Có PAD cho khuôn mặt; IAPAR nên dưới 0,07 | NIST SP 800-63B-4, mục 3.2.3 | Có PAD; IAPAR: {điền theo kết quả} | `DeepFacePad.score` và bước kiểm `pad_threshold` trong `AuthSystem.verify`; IAPAR toàn luồng trong `TH10_bao-cao-deepface.json` |
| Giới hạn số lần xác thực sai liên tiếp | NIST SP 800-63B-4, mục 3.2.3 | Có | `DecisionPolicy.max_failures = 5`; chuỗi `chuoi_khoa_tai_khoan` trong báo cáo ghi "tài khoản đang bị khoá" sau 5 lần sai |
| Mẫu sinh trắc có thể thu hồi và không thể liên kết | ISO/IEC 24745:2022 | Có, theo số đo ở TH09, chưa đo lại ở TH10 | BioHash m = 128: tương đồng mẫu cũ với token mới là 0,503, AUC liên kết chéo 0,496 (TH09a, dữ liệu tổng hợp) |
| Xử lý dữ liệu sinh trắc học như dữ liệu cá nhân nhạy cảm | Luật 91/2025/QH15 (Điều 31); Nghị định 356/2025/NĐ-CP | Một phần | Kho chỉ chứa BioHash, nhật ký không ghi ảnh hay embedding (`AuditLog`), dùng mã giả danh, xoá dữ liệu cuối buổi; còn thiếu cơ chế người dùng yêu cầu xoá và mã hoá kho mẫu |

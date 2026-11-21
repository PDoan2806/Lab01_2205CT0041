# Phần đánh giá & thực nghiệm – TH10
**Học phần 04211 Bảo mật sinh trắc – Bài tập nhóm**

*Kết quả chạy chế độ `--deepface` với Facenet512 + opencv, 15 người đăng ký.*

---

## 1. Giao thức đánh giá

| Mục | Giá trị |
|---|---|
| Nguồn dữ liệu | Ảnh LFW (`lfw_funneled`), 30 người có nhiều ảnh nhất, mã giả danh P01–P30; P01–P15 ước lượng vector trung bình, P16–P30 đăng ký |
| Số người đăng ký | 15 người |
| Số ảnh đăng ký mỗi người | 3 ảnh |
| Số lần thử cùng người | 45 |
| Số lần thử khác người (mỗi kịch bản token) | 75 |
| Chủng loại PAI | `attack_print` và `attack_replay` (mô phỏng từ TH08) |
| Số lần tấn công mỗi loài | 45 |
| Số lần tấn công toàn luồng (IAPAR) | 90 (kẻ tấn công có token của nạn nhân) |
| Mô hình trích đặc trưng | Facenet512 |
| Bộ phát hiện | opencv |
| Số bit BioHash | 128 |
| Ngưỡng so khớp | Chọn theo EER kịch bản mất token |

---

## 2. Kết quả so sánh hai ngưỡng PAD

### Bảng tổng hợp

| Chỉ số | Ngưỡng PAD = 0.5 | Ngưỡng PAD = 0.7 | Nhận xét |
|--------|------------------|------------------|----------|
| EER token bí mật | 2,44% | 2,44% | Không đổi (không phụ thuộc PAD) |
| EER mất token | 4,89% | 4,89% | Không đổi |
| Ngưỡng so khớp đã chọn | 0,6406 | 0,6406 | Theo EER mất token |
| APCER (in) | 0,00% | 0,00% | Chặn tốt tấn công in |
| APCER (phát lại) | **65,38%** | **42,31%** | Tăng ngưỡng giảm APCER replay |
| APCER lớn nhất | 65,38% | 42,31% | |
| BPCER | 6,67% | **15,56%** | Tăng ngưỡng làm tăng từ chối thật |
| FTA (bona / print / replay) | 0 / 0 / 19 | 0 / 0 / 19 | Replay có nhiều ảnh không detect mặt |
| FRR toàn luồng | 11,11% | 20,0% | |
| **IAPAR toàn luồng** | **16,67%** | **11,11%** | Ngưỡng cao hơn an toàn hơn |
| Thời gian xác minh TB | 0,288 s | 0,34 s | |

### Nhận xét

- **Ngưỡng PAD = 0.5**: BPCER và FRR thấp hơn (trải nghiệm người dùng tốt hơn), nhưng APCER replay rất cao (65,38%) và IAPAR 16,67%.
- **Ngưỡng PAD = 0.7**: APCER replay giảm xuống 42,31% và IAPAR giảm còn 11,11%, nhưng BPCER tăng lên 15,56% và FRR tăng lên 20%.
- Cả hai ngưỡng đều có **IAPAR > 7%** (mức khuyến nghị của NIST và FIDO BioLevel 2).
- Tấn công in bị chặn gần như hoàn toàn ở cả hai ngưỡng; điểm yếu chính là tấn công phát lại (replay).

**Lựa chọn đề xuất cho báo cáo chính**: Ngưỡng **0.7** (ưu tiên an toàn hơn trước tấn công).

---

## 3. Kết quả chính dùng trong báo cáo
*(Dùng ngưỡng PAD = 0.7)*

| Chỉ số | Giá trị | Ghi chú |
|--------|---------|---------|
| EER so khớp đã bảo vệ, token bí mật | 2,44% | |
| EER so khớp đã bảo vệ, mất token | 4,89% | ngưỡng so khớp đã chọn: 0,6406 |
| APCER theo từng chủng loại PAI | in: 0,00%; phát lại: 42,31% | |
| APCER lớn nhất | 42,31% | |
| BPCER | 15,56% | |
| FTA | bona_fide: 0/45; print: 0/45; replay: 19/45 | ảnh FTA loại khỏi APCER và BPCER |
| FRR toàn luồng | 20,0% | |
| IAPAR toàn luồng | 11,11% | trên 90 lần tấn công |
| Thời gian một lần xác minh | 0,34 giây | |

Độ tin cậy: với 90 lần tấn công, cận trên 95% của IAPAR khi không có lần nào lọt khoảng 3,3%. Ở đây có khoảng 10 lần lọt nên khoảng tin cậy còn rộng. Ảnh tấn công chỉ là mô phỏng nên kết quả mang tính tham khảo.

---

## 4. Trả lời câu hỏi phân tích

**1.** Hệ thống thoả yêu cầu của NIST một phần. BioHash cần cả khuôn mặt lẫn token nên là hai yếu tố, và ngưỡng so khớp được chọn theo kịch bản mất token (0,6406) nên an toàn không dựa vào việc token còn bí mật, đúng với quan điểm sinh trắc không phải là bí mật. Tuy nhiên token hiện chỉ là một chuỗi trong chương trình, chưa gắn với một thiết bị xác thực vật lý như NIST yêu cầu. Token đóng vai trò yếu tố sở hữu và là hạt giống của ma trận chiếu. Đổi token là thu hồi được mẫu (ở TH09a, tương đồng mẫu cũ với token mới ≈ 0,503, gần như khác người).

**2.** IAPAR toàn luồng của nhóm là **11,11%** (ngưỡng PAD 0.7) trên 90 lần tấn công, **cao hơn** mức khuyến nghị 0,07 của NIST SP 800-63B-4 và mức 7% của FIDO cho BioLevel 2. Với 90 lần thử thì chưa kết luận chắc được. Ảnh tấn công chỉ là mô phỏng từ 15 người nên số liệu chỉ mang tính tham khảo. Khi dùng ngưỡng PAD 0.5 thì IAPAR còn cao hơn (16,67%).

**3.** Khoá sau 5 lần sai giúp chặn kẻ đoán liên tục, nhưng cho kẻ gian một đường khác: cố tình thử sai 5 lần để khoá tài khoản của nạn nhân. Mã còn tính cả lần bị PAD từ chối là một lần sai, không có thời hạn mở khoá, và bộ đếm nằm trong bộ nhớ nên mất khi khởi động lại. Đề xuất: khoá tạm, tăng dần theo số lần, đếm theo thiết bị, mở khoá bằng một yếu tố khác và báo cho chủ tài khoản.

**4.** Nếu kho mẫu lộ nhưng khoá HMAC và token không lộ: kẻ tấn công đọc được chuỗi 128 bit BioHash nhưng không sửa được kho (HMAC phát hiện), không có token nên không so khớp được, và không biết embedding hay ảnh. Nếu cả token cũng lộ: thành công phụ thuộc vào IAPAR (11,11%) và chính sách khoá; kẻ tấn công có thể thử nhiều ảnh cho tới khi ra chuỗi bit gần mẫu. Nếu khoá HMAC cũng lộ thì kẻ tấn công thay được mẫu của nạn nhân bằng mẫu của mình.

**5.** Ba quyết định thiết kế giảm rủi ro cho người có dữ liệu (dữ liệu sinh trắc là dữ liệu cá nhân nhạy cảm theo Luật 91/2025/QH15 và Nghị định 356/2025/NĐ-CP):
- (a) Kho mẫu chỉ chứa BioHash đã biến đổi bằng token, không lưu ảnh hay embedding → thu hồi được bằng đổi token.
- (b) Nhật ký `AuditLog` chỉ ghi sự kiện, điểm và mã giả danh, không chứa dữ liệu sinh trắc.
- (c) Token để ở thiết bị người dùng, khoá HMAC để ngoài mã nguồn → người quản trị kho một mình không so khớp thay người dùng được.

---

## 5. Hạn chế và việc cần làm tiếp

1. Ảnh tấn công chỉ là mô phỏng (TH08), chưa phải ảnh chụp lại qua giấy in hay màn hình thật.
2. Cỡ mẫu còn nhỏ (15 người, 90 lần tấn công) → khoảng tin cậy rộng.
3. APCER replay vẫn cao (42–65%) → cần cải thiện PAD hoặc thêm thách thức–phản hồi.
4. Chính sách khoá dễ bị lợi dụng để khoá tài khoản người khác.
5. Khoá HMAC mặc định nằm trong mã nếu không đặt biến môi trường `TH10_STORE_KEY`.

---

*File này dùng để điền vào `bao-cao-nhom.md` và hỗ trợ trình bày.*

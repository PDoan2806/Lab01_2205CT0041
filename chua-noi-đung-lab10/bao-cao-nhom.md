# Báo cáo đánh giá hệ thống xác thực khuôn mặt, nhóm {số nhóm}

Học phần 04211 Bảo mật sinh trắc, bài TH10.

## 1. Thành viên và phân công

| Mã sinh viên | Vai trò | Phần việc cụ thể (hàm, mục báo cáo) | Tỷ lệ đóng góp do nhóm thống nhất |
|---|---|---|---|
| {mã} | trưởng nhóm tích hợp | {ví dụ: `AuthSystem`, `run_deepface`, nộp bài lên kho} | {%} |
| {mã} | phụ trách đánh giá | {ví dụ: chạy `--deepface`, mục 3 và 4 của báo cáo} | {%} |
| {mã} | phụ trách bảo mật, mô hình đe doạ | {ví dụ: `TemplateStore`, `DecisionPolicy`, `mo-hinh-de-doa.md`} | {%} |
| {mã} | phụ trách trình bày | {ví dụ: `trinh-bay.pdf`, mục 5 và 6 của báo cáo} | {%} |

## 2. Kiến trúc và các lựa chọn thiết kế

Sơ đồ khối của luồng xác minh (theo `AuthSystem.verify`):

```
khung hình --> PAD (DeepFacePad) --> trích đặc trưng (DeepFaceEmbedder)
          --> BioHash (BioHashProtector, token của người dùng)
          --> so khớp với mẫu trong kho (TemplateStore, kiểm HMAC)
          --> chính sách (DecisionPolicy: ngưỡng, khoá sau 5 lần sai) --> quyết định
mọi sự kiện --> AuditLog (nhật ký chỉ ghi thêm, không chứa dữ liệu sinh trắc)
```

| Lựa chọn | Giá trị | Lý do (dẫn số đo) |
|---|---|---|
| Mô hình trích đặc trưng và bộ phát hiện | Facenet512, opencv {đổi nếu nhóm chọn khác ở TH04} | {dẫn số đo của TH04}. Bộ phát hiện opencv nhanh hơn RetinaFace, vốn chạy chậm ở TH04 |
| Ngưỡng PAD | 0,5 {hoặc giá trị nhóm đặt bằng `--pad-threshold`} | Ở TH08 (dữ liệu mô phỏng), ngưỡng 0,3 / 0,5 / 0,7 cho APCER lớn nhất 88,89% / 77,78% / 27,78% và BPCER 6,67% / 13,33% / 23,33%. {nhóm giải thích vì sao giữ hoặc đổi} |
| Số bit BioHash | 128 | Ở TH09a, EER khi mất token là 19,77% (32 bit), 11,70% (64 bit), 6,35% (128 bit): càng nhiều bit càng đỡ khi mất token |
| Nơi lưu token, nơi lưu khoá HMAC | Token trên thiết bị người dùng, không vào kho mẫu; khoá HMAC trong biến môi trường `TH10_STORE_KEY`, không ghi vào mã hay Git | Kho bị lộ thì kẻ tấn công vẫn thiếu token để so khớp (bài học BioHashing, TH09); khoá HMAC để ngoài mã để không lộ cùng kho mã |
| Ngưỡng so khớp (chọn theo kịch bản nào) | Ngưỡng tại EER của kịch bản mất token (`e_stolen["threshold"]`) | An ninh phải đứng vững khi yếu tố sở hữu đã bị lộ |
| Số lần sai trước khi khoá | 5 | Theo NIST SP 800-63B-4, mục 3.2.3: 5 lần sai liên tiếp (mức 10 nếu có PAD, nhóm chọn mức chặt hơn) |

## 3. Giao thức đánh giá

| Mục | Giá trị |
|---|---|
| Nguồn dữ liệu (LFW hoặc thành viên có phiếu đồng ý, mã giả danh) | Ảnh LFW (`lfw_funneled`), 20 người có nhiều ảnh nhất, mã giả danh P01 đến P20; P01 đến P10 chỉ dùng ước lượng vector trung bình, P11 đến P20 đăng ký |
| Số người đăng ký, số ảnh đăng ký mỗi người | 10 người, 3 ảnh đăng ký mỗi người {sửa nếu dùng `--n-users` khác 10} |
| Số lần thử cùng người | 30 (10 người, 3 ảnh truy vấn mỗi người) {trừ ảnh không phát hiện được mặt} |
| Số lần thử khác người (token riêng; mất token) | 50 cho mỗi kịch bản (10 người, 5 kẻ giả mạo mỗi người) |
| Chủng loại PAI và số lần tấn công mỗi loài | `attack_print` và `attack_replay`, mỗi loài 30 lần; ảnh tấn công được mô phỏng từ ảnh thật bằng hàm của TH08, chưa phải ảnh chụp lại qua giấy in hay màn hình |
| Số lần tấn công mạo danh toàn luồng (tính IAPAR) | 60 (30 ảnh in và 30 ảnh phát lại), kẻ tấn công có token của nạn nhân. Ảnh không phát hiện được mặt vẫn tính vào mẫu số |
| Máy chạy (CPU, RAM, hệ điều hành) | {điền}, Windows |

## 4. Kết quả

Số liệu lấy từ `ket-qua/TH10_bao-cao-deepface.json` do chương trình ghi ra.

| Chỉ số | Giá trị | Ghi chú |
|---|---|---|
| EER so khớp đã bảo vệ, token bí mật | {EER_so_khop_bao_ve_token_bi_mat_%} | |
| EER so khớp đã bảo vệ, mất token | {EER_so_khop_bao_ve_mat_token_%} | ngưỡng so khớp đã chọn: {nguong_so_khop_da_chon} |
| APCER theo từng chủng loại PAI | in: {…}; phát lại: {…} | {APCER_theo_loai_%} |
| APCER lớn nhất | {APCER_max_%} | |
| BPCER | {BPCER_%} | |
| Tỷ lệ không phát hiện được khuôn mặt (FTA) | {số ảnh / tổng}, từng loại: {FTA} | ảnh FTA bị loại khỏi APCER và BPCER |
| Tỷ lệ từ chối sai toàn luồng | {FRR_toan_luong_%} | |
| IAPAR toàn luồng | {IAPAR_toan_luong_%} | trên 60 lần tấn công |
| Thời gian một lần xác minh | {thoi_gian_TB_1_lan_xac_minh_s} giây | |

![Hình 1: Đường DET của so khớp BioHash khi token bí mật và khi mất token](ket-qua/TH10_det-so-khop.png)

Độ tin cậy: với số lần thử trên, mỗi con số có khoảng tin cậy rộng. Ví dụ nếu không lần nào lọt trong 30 lần tấn công thì cận trên 95% của APCER xấp xỉ 3/30 = 10%; với 60 lần tấn công toàn luồng, nếu không lần nào lọt thì cận trên của IAPAR xấp xỉ 3/60 = 5%. {nhóm viết lại theo số thật}

## 5. Trả lời câu hỏi phân tích

**1.** Hệ thống thoả yêu cầu của NIST một phần. BioHash cần cả khuôn mặt lẫn token (`BioHashProtector.protect(emb, token)`) nên là hai yếu tố, và ngưỡng so khớp được chọn theo kịch bản mất token nên an toàn không dựa vào việc token còn bí mật, đúng với quan điểm sinh trắc không phải bí mật. Nhưng token hiện chỉ là một chuỗi trong chương trình, chưa gắn với một thiết bị xác thực vật lý như NIST yêu cầu. Token đóng vai trò yếu tố sở hữu và là hạt giống của ma trận chiếu. Đổi token là thu hồi được mẫu: ở TH09a, tương đồng giữa mẫu cũ và mẫu mới với token mới là 0,503, gần như giữa hai người khác nhau (0,501).

**2.** IAPAR toàn luồng của nhóm là {X}% trên 60 lần tấn công, {thấp hơn / cao hơn} mức khuyến nghị 0,07 của NIST và mức 7% của FIDO cho BioLevel 2. Nhưng với 60 lần thử thì chưa kết luận chắc được. Nếu không lần nào lọt thì cận trên 95% là khoảng 3/60 = 5%; muốn chắc IAPAR dưới 7% khi không lần nào lọt thì cần ít nhất khoảng 43 lần tấn công, còn nếu đã có vài lần lọt thì cần nhiều hơn nhiều (ở TH08, 4 lần lọt trong 60 lần cho khoảng tin cậy 95% từ 2,6% đến 15,9%). Ảnh tấn công ở đây lại là ảnh mô phỏng từ 10 người nên con số chỉ có tính tham khảo. {nhóm điền X và sửa câu cho khớp số thật}

**3.** Khoá sau 5 lần sai giúp chặn kẻ đoán liên tục, nhưng cho kẻ gian một đường khác: cố tình thử sai 5 lần để khoá tài khoản của nạn nhân. Mã còn làm vấn đề nặng hơn: `AuthSystem.verify` tính cả lần bị PAD từ chối là một lần sai (`policy.record(user_id, False)`), nên một người đưa ảnh in 5 lần cũng khoá được nạn nhân; `DecisionPolicy.locked` không có thời hạn mở khoá nên người thật bị khoá mãi, và bộ đếm nằm trong bộ nhớ nên mất khi khởi động lại. Đề xuất: khoá tạm, tăng dần theo số lần, đếm theo thiết bị, mở khoá bằng một yếu tố khác (mật khẩu hoặc mã gửi về điện thoại) và báo cho chủ tài khoản.

**4.** Nếu kho mẫu lộ nhưng khoá HMAC và token không lộ: kẻ tấn công đọc được chuỗi 128 bit BioHash của từng người, nhưng không sửa được kho (HMAC phát hiện, như minh hoạ "Kho mẫu bị sửa đổi: từ chối xác minh"), không có token nên không tạo được mã để so khớp với mẫu, và không biết embedding hay ảnh vì kho không chứa chúng. Nếu cả token cũng lộ (HMAC vẫn kín): kẻ tấn công vẫn phải qua PAD và so khớp, tức là thành công hay không phụ thuộc vào IAPAR đo ở kịch bản mất token ({X}%) và vào việc khoá tài khoản sau 5 lần; họ có thể thử nhiều ảnh cho tới khi ra chuỗi bit gần mẫu, nên cần giới hạn số lần thử. Nếu khoá HMAC cũng lộ thì kẻ tấn công thay được mẫu của nạn nhân bằng mẫu của mình (điểm 6 trong mô hình đe doạ). Đây là lý do khoá HMAC không được dùng giá trị mặc định trong mã.

**5.** Ba quyết định thiết kế giảm rủi ro cho người có dữ liệu, gắn với việc dữ liệu sinh trắc là dữ liệu cá nhân nhạy cảm (Luật 91/2025/QH15, Điều 31; Nghị định 356/2025/NĐ-CP): (a) kho mẫu chỉ chứa BioHash đã biến đổi bằng token, không lưu ảnh hay embedding, nên kho lộ cũng không lộ khuôn mặt, và mẫu thu hồi được bằng cách đổi token; (b) nhật ký `AuditLog` chỉ ghi sự kiện, điểm và mã người dùng giả danh, không ghi ảnh, embedding hay mẫu; (c) token để ở thiết bị người dùng, còn khoá HMAC để ngoài mã nguồn, nên người quản trị kho một mình cũng không so khớp thay người dùng được. Ngoài ra, khi thử nghiệm nhóm dùng mã giả danh và xoá dữ liệu khuôn mặt cuối buổi. Cần đối chiếu thêm điều khoản cụ thể của luật và nghị định về cơ sở xử lý, đồng ý và quyền xoá dữ liệu, mà hệ thống hiện chưa có. {nhóm đọc lại điều khoản và chỉnh}

## 6. Hạn chế và việc cần làm tiếp

1. **Khoá HMAC mặc định nằm trong mã.** Nếu quên đặt `TH10_STORE_KEY` thì `TemplateStore` dùng khoá `khoa-chi-dung-khi-thu-nghiem`, ai có mã đều ký lại được kho. Việc cần làm: bắt buộc đặt biến môi trường, thiếu thì báo lỗi và dừng.
2. **HMAC không chống đưa lại kho cũ.** Phần được ký chỉ gồm các mẫu, không có số phiên bản hay thời gian, nên một kho cũ còn hợp lệ vẫn được chấp nhận. Việc cần làm: thêm số phiên bản tăng dần vào phần được ký và lưu số mới nhất ở nơi khác.
3. **Chính sách khoá dễ bị lợi dụng để khoá tài khoản người khác.** Lần PAD từ chối cũng bị tính là sai, không có thời hạn mở khoá, bộ đếm mất khi khởi động lại (xem câu 3). Việc cần làm: khoá tạm có thời hạn, lưu bộ đếm bền vững, đếm theo thiết bị.
4. **Ảnh tấn công chỉ là mô phỏng.** Ảnh in và phát lại được sinh bằng hàm của TH08, chưa phải ảnh chụp lại qua giấy in hay màn hình thật, và chưa có mặt nạ hay video do AI tạo. Việc cần làm: chụp lại bộ ảnh in và phát lại thật (có phiếu đồng ý) và đo lại APCER.
5. **Tấn công chèn dữ liệu chưa có biện pháp.** PAD ở tầng ảnh không chống được video quay sẵn (TH08: vượt thách thức 25%). Việc cần làm: ghép thách thức - phản hồi của TH08 vào trước PAD, rồi tiến tới ký khung hình ở thiết bị.
6. **Cỡ mẫu nhỏ.** 10 người đăng ký và 60 lần tấn công cho khoảng tin cậy rộng. Việc cần làm: tăng `--n-users` và số ảnh mỗi người.

## 7. Xác nhận xử lý dữ liệu

- [ ] Thư mục nộp không chứa ảnh, embedding, kho mẫu, nhật ký có mã giả danh.
- [ ] Dữ liệu khuôn mặt của thành viên (nếu có) đã xoá, biên bản xoá dữ liệu có chữ ký trợ giảng.

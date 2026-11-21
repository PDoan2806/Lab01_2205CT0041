# Báo cáo đánh giá hệ thống xác thực khuôn mặt, nhóm 5

Học phần 04211 Bảo mật sinh trắc, bài TH10.

## 1. Thành viên và phân công

| Mã sinh viên | Vai trò | Phần việc cụ thể (hàm, mục báo cáo) | Tỷ lệ đóng góp do nhóm thống nhất |
|---|---|---|---|
| 2305CT0763-Văn Thái Nguyên | trưởng nhóm tích hợp | `AuthSystem`, `run_deepface`, nộp bài lên kho | 100% |
| 2305CT2049-Hà Nguyễn Thành Trí | phụ trách đánh giá và thực nghiệm | chạy `--deepface`, mục 3 và 4 của báo cáo | 100% |
| 2305CT2058-Phạm Minh Hoàng | phụ trách bảo mật, mô hình đe doạ | `TemplateStore`, `DecisionPolicy`, `mo-hinh-de-doa.md`, câu 3 đến 5 và mục 6 của báo cáo, tổng hợp `bao-cao-nhom.md` | 100% |
| 2205CT0041-Kiều Huỳnh Phi Đoàn | phụ trách trình bày | `trinh-bay.pdf`, trình bày mục 5 và 6 của báo cáo | 100% |

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
| Mô hình trích đặc trưng và bộ phát hiện | Facenet512, MTCNN có căn chỉnh | Ở TH04 (300 cặp LFW), Facenet512 với MTCNN có căn chỉnh cho EER 2,67%, không bỏ ảnh nào (FTA = 0), 0,381 giây mỗi ảnh; với opencv EER là 9,22% và không thu nhận được 17 ảnh; RetinaFace không căn chỉnh tốt nhất (1,33%) nhưng chậm (4,058 giây mỗi ảnh). Chọn MTCNN vì cân bằng giữa độ chính xác, FTA và tốc độ |
| Ngưỡng PAD | 0,5 (lần chạy chính) | Ở TH08 (dữ liệu mô phỏng), ngưỡng 0,3 / 0,5 / 0,7 cho APCER lớn nhất 88,89% / 77,78% / 27,78% và BPCER 6,67% / 13,33% / 23,33%. Ở TH10 với ngưỡng 0,5: APCER lớn nhất 67,86%, BPCER 10,0% và IAPAR 18,33%, chưa đạt mức 7%. Nhóm đã chạy thêm ngưỡng 0,7 trên cùng dữ liệu (mục 4): APCER phát lại giảm còn 39,29% và IAPAR còn 10,0%, nhưng BPCER tăng lên 23,33%; không ngưỡng nào đạt mức 7%. Nhóm giữ 0,5 làm cấu hình đo chính để so với TH08; nếu triển khai cho giao dịch giá trị lớn nên dùng 0,7 kèm xác thực bổ sung (như đã chọn ở TH08), vì người dùng thật bị từ chối nhiều hơn. |
| Số bit BioHash | 128 | Ở TH09a, EER khi mất token là 19,77% (32 bit), 11,70% (64 bit), 6,35% (128 bit): càng nhiều bit càng đỡ khi mất token |
| Nơi lưu token, nơi lưu khoá HMAC | Token trên thiết bị người dùng, không vào kho mẫu; khoá HMAC trong biến môi trường `TH10_STORE_KEY`, không ghi vào mã hay Git | Kho bị lộ thì kẻ tấn công vẫn thiếu token để so khớp (bài học BioHashing, TH09); khoá HMAC để ngoài mã để không lộ cùng kho mã |
| Ngưỡng so khớp (chọn theo kịch bản nào) | Ngưỡng tại EER của kịch bản mất token (`e_stolen["threshold"]`) | An ninh phải đứng vững khi yếu tố sở hữu đã bị lộ |
| Số lần sai trước khi khoá | 5 | Theo NIST SP 800-63B-4, mục 3.2.3: 5 lần sai liên tiếp (mức 10 nếu có PAD, nhóm chọn mức chặt hơn) |

## 3. Giao thức đánh giá

| Mục | Giá trị |
|---|---|
| Nguồn dữ liệu (LFW hoặc thành viên có phiếu đồng ý, mã giả danh) | Ảnh LFW (`lfw_funneled`), 20 người có nhiều ảnh nhất, mã giả danh P01 đến P20; P01 đến P10 chỉ dùng ước lượng vector trung bình, P11 đến P20 đăng ký; mỗi người lấy 6 ảnh đầu theo thứ tự tên tệp |
| Số người đăng ký, số ảnh đăng ký mỗi người | 10 người, 3 ảnh đăng ký mỗi người |
| Số lần thử cùng người | 30 (10 người, 3 ảnh truy vấn mỗi người); không có ảnh thật nào bị FTA |
| Số lần thử khác người (token riêng; mất token) | 50 cho mỗi kịch bản (10 người, 5 kẻ giả mạo mỗi người) |
| Chủng loại PAI và số lần tấn công mỗi loài | `attack_print` và `attack_replay`, mỗi loài 30 lần; ảnh tấn công được mô phỏng từ ảnh thật bằng hàm của TH08, chưa phải ảnh chụp lại qua giấy in hay màn hình |
| Số lần tấn công mạo danh toàn luồng (tính IAPAR) | 60 (30 ảnh in và 30 ảnh phát lại), kẻ tấn công có token của nạn nhân. Ảnh không phát hiện được mặt vẫn tính vào mẫu số |
| Máy chạy (CPU, RAM, hệ điều hành) | intel coreI7-13620H ; Python 3.12, deepface, tensorflow, mtcnn. Hạt giống 4211 |
| Lệnh chạy | đặt `$env:TH10_STORE_KEY` là một chuỗi ngẫu nhiên, rồi `python th10_he_thong.py --deepface --detector mtcnn --n-users 10 --pad-threshold 0.5` (và `--pad-threshold 0.7` để so sánh thêm) |

## 4. Kết quả

Số liệu chính (ngưỡng PAD 0,5) lấy từ `ket-qua/TH10_bao-cao-deepface.json` (`TH10_bao-cao-deepface_2.json`) do chương trình ghi ra khi chạy `--deepface --detector mtcnn --n-users 10 --pad-threshold 0.5`; số liệu so sánh ngưỡng 0,7 lấy từ `TH10_bao-cao-deepface_3.json` (cùng cấu hình, thêm `--pad-threshold 0.7`).

| Chỉ số | Giá trị | Ghi chú |
|---|---|---|
| EER so khớp đã bảo vệ, token bí mật | 0,00% | 30 cặp cùng người và 50 cặp khác người tách hẳn nhau trong mẫu này; với cỡ mẫu nhỏ, EER 0% chỉ cho biết FNMR nhỏ hơn khoảng 10% |
| EER so khớp đã bảo vệ, mất token | 3,67% | ngưỡng so khớp đã chọn: 0,6719 |
| APCER theo từng chủng loại PAI | in: 0,00% (0/30); phát lại: 67,86% (19/28) | 2 ảnh phát lại không phát hiện được mặt nên bị loại khỏi mẫu số; nếu tính chúng là bị chặn thì APCER phát lại là 63,33% (19/30) |
| APCER lớn nhất | 67,86% | loài phát lại; khoảng tin cậy Wilson 95% từ 49,3% đến 82,1% |
| BPCER | 10,00% (3/30) | khoảng tin cậy Wilson 95% từ 3,5% đến 25,6% |
| Tỷ lệ không phát hiện được khuôn mặt (FTA) | 2/90 ảnh (2,2%): thật 0/30, in 0/30, phát lại 2/30 | ảnh FTA bị loại khỏi APCER và BPCER, nhưng tính là bị từ chối ở toàn luồng |
| Tỷ lệ từ chối sai toàn luồng | 13,33% (4/30) | 3 lần do PAD từ chối ảnh thật, 1 lần do so khớp |
| IAPAR toàn luồng | 30,00% (18/60) | ảnh in 0/30, ảnh phát lại 18/30; khoảng tin cậy Wilson 95% từ 19,9% đến 42,5% |
| Thời gian một lần xác minh | 0,529 giây | trung bình thời gian PAD cộng thời gian trích đặc trưng mỗi ảnh trên Gigabyte G6 (2024) (lần chạy trước: 0,496 giây) |

So sánh hai ngưỡng PAD trên cùng dữ liệu và cùng ngưỡng so khớp 0,6719 (EER so khớp không đổi vì không phụ thuộc PAD):

| Chỉ số | PAD 0,5 | PAD 0,7 |
|---|---|---|
| APCER ảnh in | 0,00% (0/30) | 0,00% (0/30) |
| APCER ảnh phát lại | 67,86% (19/28) | 39,29% (11/28) |
| BPCER | 10,00% (3/30) | 23,33% (7/30) |
| Tỷ lệ từ chối sai toàn luồng | 13,33% (4/30) | 26,67% (8/30) |
| IAPAR toàn luồng | 30,00% (18/60) | 18,33% (11/60) |
| Khoảng tin cậy Wilson 95% của IAPAR | 19,9% đến 42,5% | 10,6% đến 29,9% |
| Thời gian một lần xác minh | 0,529 giây | 0,587 giây |

Nâng ngưỡng PAD từ 0,5 lên 0,7 giúp APCER ảnh phát lại giảm từ 67,86% xuống 39,29% và IAPAR toàn luồng giảm từ 30,00% xuống 18,33%, nhưng đồng thời làm BPCER tăng từ 10,00% lên 23,33% và tỷ lệ từ chối sai toàn luồng tăng từ 13,33% lên 26,67%; ở cả hai ngưỡng, cận dưới khoảng tin cậy 95% của IAPAR đều cao hơn mức khuyến nghị 7% của NIST/FIDO nên chưa đạt yêu cầu.

![Hình 1: Đường DET của so khớp BioHash khi token bí mật và khi mất token](hinh/TH10_det-so-khop.png)

Ghi chú Hình 1: ở kịch bản token bí mật, điểm cùng người và khác người tách hẳn nhau (EER 0%) nên đường DET trùng với trục và gần như không nhìn thấy; đường nhìn thấy được là kịch bản mất token.

Độ tin cậy: với cỡ mẫu này, mỗi con số có khoảng tin cậy rộng (Wilson 95%): IAPAR toàn luồng 30,00% nằm trong khoảng 19,9% đến 42,5% (ở ngưỡng 0,7 là 18,33% trong khoảng 10,6% đến 29,9%); APCER phát lại 67,86% trong khoảng 49,3% đến 82,1%; BPCER 10,0% trong khoảng 3,5% đến 25,6%. Với ảnh in, 0/30 lần lọt chỉ cho biết APCER thực nhỏ hơn khoảng 10% (3/30). Các lần thử không hoàn toàn độc lập vì ảnh tấn công được mô phỏng từ ảnh thật của 10 người.

## 5. Trả lời câu hỏi phân tích

**1.** Hệ thống thoả yêu cầu của NIST một phần. BioHash cần cả khuôn mặt lẫn token (`BioHashProtector.protect(emb, token)`) nên là hai yếu tố, và ngưỡng so khớp được chọn theo kịch bản mất token nên an toàn không dựa vào việc token còn bí mật, đúng với quan điểm sinh trắc không phải bí mật. Nhưng token hiện chỉ là một chuỗi trong chương trình, chưa gắn với một thiết bị xác thực vật lý như NIST yêu cầu. Token đóng vai trò yếu tố sở hữu và là hạt giống của ma trận chiếu. Đổi token là thu hồi được mẫu: ở TH09a, tương đồng giữa mẫu cũ và mẫu mới với token mới là 0,503, gần như giữa hai người khác nhau (0,501).

**2.** IAPAR toàn luồng của nhóm là 18,33% (11/60 lần tấn công), cao hơn mức khuyến nghị 0,07 của NIST và mức 7% của FIDO cho BioLevel 2. Với số lần đã thử, nhóm kết luận được là hệ thống chưa đạt: cận dưới của khoảng tin cậy Wilson 95% là 10,6%, vẫn trên 7%. Cả 11 lần lọt đều là ảnh phát lại (11/30); ảnh in bị PAD chặn hết (0/30). Ngược lại, nếu kết quả đạt thì 60 lần vẫn chưa đủ để kết luận: ngay cả khi không lần nào lọt, cận trên 95% vẫn khoảng 3/60 = 5%, và muốn chắc IAPAR dưới 7% cần ít nhất khoảng 43 lần tấn công độc lập mà không lần nào lọt (ở TH08, 4 lần lọt trong 60 lần cho khoảng tin cậy 95% từ 2,6% đến 15,9%). Ở ngưỡng PAD 0,7, IAPAR giảm còn 10,0% (6/60, khoảng tin cậy 4,7% đến 20,1%): cận dưới thấp hơn 7% nên với 60 lần thử không kết luận được nó vượt hay đạt mức 7%, và cái giá là BPCER tăng lên 23,33%. Ảnh tấn công là ảnh mô phỏng từ 10 người nên con số chỉ có tính tham khảo.

**3.** Khoá sau 5 lần sai giúp chặn kẻ đoán liên tục, nhưng cho kẻ gian một đường khác: cố tình thử sai 5 lần để khoá tài khoản của nạn nhân. Mã còn làm vấn đề nặng hơn: `AuthSystem.verify` tính cả lần bị PAD từ chối là một lần sai (`policy.record(user_id, False)`), nên một người đưa ảnh in 5 lần cũng khoá được nạn nhân; `DecisionPolicy.locked` không có thời hạn mở khoá nên người thật bị khoá mãi, và bộ đếm nằm trong bộ nhớ nên mất khi khởi động lại. Đề xuất: khoá tạm, tăng dần theo số lần, đếm theo thiết bị, mở khoá bằng một yếu tố khác (mật khẩu hoặc mã gửi về điện thoại) và báo cho chủ tài khoản.

**4.** Nếu kho mẫu lộ nhưng khoá HMAC và token không lộ: kẻ tấn công đọc được chuỗi 128 bit BioHash của từng người, nhưng không sửa được kho (HMAC phát hiện, như minh hoạ "Kho mẫu bị sửa đổi: từ chối xác minh"), không có token nên không tạo được mã để so khớp với mẫu, và không biết embedding hay ảnh vì kho không chứa chúng. Nếu cả token cũng lộ (HMAC vẫn kín): kẻ tấn công vẫn phải qua PAD và so khớp, tức là thành công hay không phụ thuộc vào IAPAR đo ở kịch bản mất token (18,33%) và vào việc khoá tài khoản sau 5 lần; họ có thể thử nhiều ảnh cho tới khi ra chuỗi bit gần mẫu, nên cần giới hạn số lần thử. Nếu khoá HMAC cũng lộ thì kẻ tấn công thay được mẫu của nạn nhân bằng mẫu của mình (điểm 6 trong mô hình đe doạ). Đây là lý do khoá HMAC không được dùng giá trị mặc định trong mã.

**5.** Ba quyết định thiết kế giảm rủi ro cho người có dữ liệu, gắn với việc dữ liệu sinh trắc là dữ liệu cá nhân nhạy cảm (Luật 91/2025/QH15, Điều 31; Nghị định 356/2025/NĐ-CP): (a) kho mẫu chỉ chứa BioHash đã biến đổi bằng token, không lưu ảnh hay embedding, nên kho lộ cũng không lộ khuôn mặt, và mẫu thu hồi được bằng cách đổi token; (b) nhật ký `AuditLog` chỉ ghi sự kiện, điểm và mã người dùng giả danh, không ghi ảnh, embedding hay mẫu; (c) token để ở thiết bị người dùng, còn khoá HMAC để ngoài mã nguồn, nên người quản trị kho một mình cũng không so khớp thay người dùng được. Ngoài ra, khi thử nghiệm nhóm chỉ dùng ảnh LFW công khai với mã giả danh P01 đến P20, và không đưa ảnh, embedding, kho mẫu hay nhật ký lên kho. Điều 31 của Luật là điều riêng về bảo vệ dữ liệu vị trí cá nhân và dữ liệu sinh trắc học, và Nghị định 356/2025/NĐ-CP xếp dữ liệu sinh trắc học vào dữ liệu cá nhân nhạy cảm. Hệ thống hiện chưa có cơ chế để người dùng yêu cầu xoá dữ liệu và chưa mã hoá kho mẫu (xem mục 6).

## 6. Hạn chế và việc cần làm tiếp

1. **Khoá HMAC mặc định nằm trong mã.** Nếu quên đặt `TH10_STORE_KEY` thì `TemplateStore` dùng khoá `khoa-chi-dung-khi-thu-nghiem`, ai có mã đều ký lại được kho. Việc cần làm: bắt buộc đặt biến môi trường, thiếu thì báo lỗi và dừng.
2. **HMAC không chống đưa lại kho cũ.** Phần được ký chỉ gồm các mẫu, không có số phiên bản hay thời gian, nên một kho cũ còn hợp lệ vẫn được chấp nhận. Việc cần làm: thêm số phiên bản tăng dần vào phần được ký và lưu số mới nhất ở nơi khác.
3. **Chính sách khoá dễ bị lợi dụng để khoá tài khoản người khác.** Lần PAD từ chối cũng bị tính là sai, không có thời hạn mở khoá, bộ đếm mất khi khởi động lại (xem câu 3). Việc cần làm: khoá tạm có thời hạn, lưu bộ đếm bền vững, đếm theo thiết bị.
4. **Ảnh tấn công chỉ là mô phỏng.** Ảnh in và phát lại được sinh bằng hàm của TH08, chưa phải ảnh chụp lại qua giấy in hay màn hình thật, và chưa có mặt nạ hay video do AI tạo. Việc cần làm: chụp lại bộ ảnh in và phát lại thật (có phiếu đồng ý) và đo lại APCER.
5. **Tấn công chèn dữ liệu chưa có biện pháp.** PAD ở tầng ảnh không chống được video quay sẵn (TH08: vượt thách thức 12,5% và 25% ở hai lần chạy, quanh mức đoán mò 12,5%). Việc cần làm: ghép thách thức - phản hồi của TH08 vào trước PAD, rồi tiến tới ký khung hình ở thiết bị.
6. **Cỡ mẫu nhỏ.** 10 người đăng ký và 60 lần tấn công cho khoảng tin cậy rộng. Việc cần làm: tăng `--n-users` và số ảnh mỗi người.
7. **PAD thật chưa đạt mục tiêu.** Ở ngưỡng 0,5, IAPAR toàn luồng là 18,33% và APCER ảnh phát lại là 67,86%; nâng lên 0,7 giảm IAPAR còn 10,0% và APCER phát lại còn 39,29% nhưng BPCER tăng từ 10% lên 23,33%, nên không ngưỡng nào đạt cả hai mục tiêu. Ảnh LFW là ảnh tĩnh nhỏ nên BPCER cũng chỉ mang tính minh hoạ. Việc cần làm: thử mô hình PAD mạnh hơn hoặc ghép thách thức - phản hồi để giảm APCER mà không tăng BPCER, chọn ngưỡng theo APCER mục tiêu không quá 5%, và thu ảnh phát lại thật.

## 7. Xác nhận xử lý dữ liệu

- [x] Thư mục nộp không chứa ảnh, embedding, kho mẫu, nhật ký có mã giả danh.
- [x] Không áp dụng: nhóm chỉ dùng ảnh LFW công khai, không dùng ảnh khuôn mặt của thành viên, nên không có biên bản xoá dữ liệu.

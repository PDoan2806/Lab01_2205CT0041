### Bảng tổng hợp các lựa chọn thiết kế

| Lựa chọn | Giá trị | Lý do (dẫn số đo) |
|---|---|---|
| Mô hình trích đặc trưng và bộ phát hiện | `Facenet512` (512 chiều), bộ phát hiện `opencv` | Từ kết quả TH04, `Facenet512` cho độ tách biệt đặc trưng cao nhất (EER so khớp gốc rất thấp, đạt `0.0%` khi kết hợp BioHash token bí mật) trong khi `opencv` đảm bảo tốc độ phát hiện nhanh, giữ tổng thời gian 1 lần xác minh ở mức `0.349s`. |
| Ngưỡng PAD | `0.5` | Dựa trên điểm tin cậy chuẩn hoá từ MiniFASNet (`antispoof_score` trong TH08): ngưỡng `0.5` giúp chặn đứng `100%` tấn công ảnh in (`APCER = 0.0%`) mà vẫn duy trì tỷ lệ từ chối nhầm người thật ở mức thấp (`BPCER = 3.57%`). |
| Số bit BioHash | `128` bit (trừ vector trung bình ước lượng từ 10 người ngoài danh sách đăng ký) | Từ thực nghiệm TH09a, 128 bit qua phép trực giao QR cân bằng tốt giữa tính không thể đảo ngược (giảm từ 512 số thực xuống 128 bit) và độ chính xác nhận dạng. Vector trung bình ước lượng trên tập người không đăng ký (`pop`) để tránh làm mất đặc trưng phân biệt của người dùng thật. |
| Nơi lưu token, nơi lưu khoá HMAC | Token lưu cục bộ phía người dùng (không lưu trong CSDL); Khoá HMAC lưu ở biến môi trường `TH10_STORE_KEY` | Tách biệt yếu tố sở hữu (token) khỏi kho lưu trữ trung tâm (`TH10_deepface_kho-mau.json`) để đảm bảo tính huỷ bỏ được (revocability). Khoá HMAC tách khỏi mã nguồn/Git nhằm chống giả mạo chữ ký xác thực tính toàn vẹn kho mẫu. |
| Ngưỡng so khớp (chọn theo kịch bản nào) | `0.625` (chế độ DeepFace) / `0.6094` (chế độ Mock) — chọn theo **kịch bản mất token (stolen-token)** | An ninh hệ thống phải đứng vững ngay cả khi yếu tố sở hữu (token) của nạn nhân bị lộ cho kẻ tấn công. Tại ngưỡng `0.625`, EER kịch bản mất token đạt `7.57%`. |
| Số lần sai trước khi khoá | `5` lần thử sai liên tiếp | Tuân thủ khuyến nghị của NIST SP 800-63B-4 (mục 3.2.3) về giới hạn số lần thử thất bại liên tiếp nhằm ngăn chặn tấn công dò thử trực tuyến (brute-force/hill-climbing). |

## 3. Giao thức đánh giá

| Mục | Giá trị |
|---|---|
| Nguồn dữ liệu (LFW hoặc thành viên có phiếu đồng ý, mã giả danh) | Bộ dữ liệu khuôn mặt chuẩn **LFW** (`lfw_funneled`), sử dụng mã giả danh `P01`–`P20` (10 người đầu `P01`–`P10` dùng để ước lượng vector trung bình; 10 người sau `P11`–`P20` đăng ký vào hệ thống). |
| Số người đăng ký, số ảnh đăng ký mỗi người | Chế độ `--deepface`: **10 người** đăng ký (`UP11`–`UP20`), **3 ảnh** đăng ký / người.<br>Chế độ `--mock`: **50 người** đăng ký (`U10`–`U59`), **3 ảnh** đăng ký / người. |
| Số lần thử cùng người | **30 lần** ở chế độ `--deepface` (10 người × 3 ảnh truy vấn); **150 lần** ở chế độ `--mock` (50 người × 3 ảnh truy vấn). |
| Số lần thử khác người (token riêng; mất token) | **50 cặp** mỗi kịch bản ở chế độ `--deepface` (10 người × 5 người khác ngẫu nhiên); **250 cặp** mỗi kịch bản ở chế độ `--mock`. |
| Chủng loại PAI và số lần tấn công mỗi loài | 2 chủng loại mô phỏng từ TH08 (`tao_du_lieu_pad_mau.py`):<br>- **Ảnh in (`attack_print`)**: 30 lần thử (10 nạn nhân × 3 ảnh).<br>- **Ảnh phát lại qua màn hình (`attack_replay`)**: 30 lần thử (10 nạn nhân × 3 ảnh). |
| Số lần tấn công mạo danh toàn luồng (tính IAPAR) | **60 lần** tấn công toàn luồng ở chế độ `--deepface` (30 `attack_print` + 30 `attack_replay`, kẻ tấn công sử dụng ảnh của nạn nhân và nắm giữ **token của nạn nhân**). |
| Máy chạy (CPU, RAM, hệ điều hành) | Apple MacBook Pro (Chip Apple M1, macOS, Python 3.12/3.13, TensorFlow/DeepFace). |

## 4. Kết quả

### Bảng tổng hợp chỉ số đánh giá (Chế độ `--deepface` và đối chiếu `--mock`)

| Chỉ số | Giá trị (`--deepface`) | Giá trị (`--mock`) | Ghi chú |
|---|---|---|---|
| EER so khớp đã bảo vệ, token bí mật | **0.0%** | 0.87% | Tách biệt hoàn toàn giữa người thật và kẻ mạo danh khi token không bị lộ. |
| EER so khớp đã bảo vệ, mất token | **7.57%** | 2.33% | Khi kẻ gian có token của nạn nhân, BioHash chỉ còn dựa vào đặc trưng khuôn mặt. |
| APCER theo từng chủng loại PAI | - `attack_print`: **0.0%** (0/28)<br>- `attack_replay`: **44.44%** (8/18) | - Mô phỏng chung: 26.67% | Tính trên các mẫu phát hiện được khuôn mặt (trừ FTA). MiniFASNet bắt tốt ảnh in nhưng yếu trước ảnh phát lại màn hình. |
| APCER lớn nhất ($\text{APCER}_{\max}$) | **44.44%** | 26.67% | Lấy giá trị xấu nhất theo chủng loại PAI (`attack_replay`). |
| BPCER | **3.57%** (1/28) | 0.0% | 1 mẫu trình diện thật bị PAD từ chối nhầm trong tổng số 28 mẫu phát hiện được mặt. |
| Tỷ lệ không phát hiện được khuôn mặt (FTA) | - `bona_fide`: **2/30** (6.67%)<br>- `attack_print`: **2/30** (6.67%)<br>- `attack_replay`: **12/30** (40.0%) | 0% (không mô phỏng lỗi phát hiện) | Bộ phát hiện `opencv` bỏ sót nhiều khuôn mặt ở ảnh `attack_replay` do nhiễu moiré và lóa màn hình. |
| Tỷ lệ từ chối sai toàn luồng (FRR) | **16.67%** (5/30) | 2.67% | Bao gồm 2 lần lỗi FTA, 1 lần lỗi BPCER của PAD và 2 lần không đạt ngưỡng so khớp `0.625`. |
| IAPAR toàn luồng | **11.67%** (7/60) | 28.0% | Trong 60 lần tấn công có kèm token nạn nhân, 7 lần vượt qua cả PAD và ngưỡng so khớp (đều thuộc `attack_replay`). |
| Thời gian một lần xác minh | **0.349 giây** | < 0.001 giây | Trung bình cộng thời gian chạy `DeepFacePad` và `DeepFaceEmbedder`. |

### Đánh giá độ tin cậy thống kê và phân tích kết quả

- **Độ tin cậy theo quy tắc số 3 (Rule of Three):**
  - Với `attack_print` đạt `0` lần lọt trên `28` mẫu hợp lệ ($N=28$), cận trên khoảng tin cậy 95% của tỷ lệ lỗi thực tế là $3 / 28 \approx \mathbf{10.71\%}$.
  - Với toàn luồng tấn công ($N=60$ lần thử, $7$ lần lọt), khoảng tin cậy 95% (Wilson/nhị thức) cho `IAPAR = 11.67%` dao động trong khoảng từ **5.8% đến 22.2%**. Số lượng 60 lần thử đủ để nhận diện xu hướng lỗ hổng ở kênh `attack_replay`, nhưng cần mở rộng lên $\ge 500$ mẫu thực tế để đạt độ phân giải dưới 1%.
- **Kiểm thử chức năng bảo mật:**
  - *Chính sách khoá tài khoản:* Khi kẻ gian thử liên tục bằng khuôn mặt và token sai vào tài khoản nạn nhân, hệ thống trả về điểm so khớp thấp (`0.453 < 0.625`) trong 5 lần đầu và tự động khoá tài khoản (`"tài khoản đang bị khoá"`) ở lần thứ 6 và thứ 7.
  - *Kiểm tra toàn vẹn kho mẫu:* Khi đảo ngược chuỗi bit của một bản ghi trong tệp JSON kho mẫu, hàm `TemplateStore.get` phát hiện sai lệch mã xác thực HMAC-SHA256 và lập tức ngắt luồng với thông báo `"Kho mẫu bị sửa đổi: từ chối xác minh"`.

*(Ghi chú: Đính kèm biểu đồ đường DET phần so khớp từ thư mục `ket-qua/` nếu xuất hình ảnh bổ sung).*

## 5. Trả lời câu hỏi phân tích

1. **Sự phù hợp với NIST SP 800-63B-4 và vai trò của token BioHash:**
   Hệ thống của nhóm **thoả mãn** nguyên tắc xác thực đa yếu tố của NIST SP 800-63B-4 ở khía cạnh coi đặc điểm sinh trắc học không phải là bí mật và kết hợp nó với một yếu tố sở hữu độc lập. Trong thiết kế này, **token BioHash** đóng vai trò là yếu tố sở hữu (something you have) được lưu tách biệt trên thiết bị người dùng, dùng làm hạt giống sinh ma trận chiếu trực giao ngẫu nhiên $Q$. Nhờ có token, vector đặc trưng khuôn mặt thô được biến đổi thành chuỗi bit bảo vệ không thể đảo ngược, đảm bảo tính huỷ bỏ được (revocability — có thể cấp token mới khi lộ mẫu) và ngăn chặn liên kết chéo giữa các cơ sở dữ liệu khác nhau.

2. **So sánh IAPAR toàn luồng với khuyến nghị của NIST SP 800-63B-4 và FIDO BioLevel 2:**
   Cả NIST SP 800-63B-4 và tiêu chuẩn FIDO Biometrics Requirements v4.0 (BioLevel 2) đều yêu cầu $\text{IAPAR} \le 7\%$ ($0.07$). Kết quả $\text{IAPAR} = \mathbf{11.67\%}$ (7/60 lần lọt) của hệ thống hiện **chưa đạt** mức khuyến nghị này, nguyên nhân chính đến từ việc mô-đun PAD để lọt nhiều mẫu tấn công phát lại màn hình (`attack_replay` có $\text{APCER} = 44.44\%$). Ngoài ra, với quy mô thử nghiệm chỉ $N = 60$ lần tấn công, sai số lấy mẫu còn lớn (khoảng tin cậy 95% lên tới 22.2%), nên nhóm **chưa thể kết luận** hệ thống đạt chuẩn an toàn thương mại; cần tập dữ liệu tấn công lớn hơn (tối thiểu vài trăm mẫu đa dạng thiết bị) để đánh giá chính xác.

3. **Rủi ro từ chính sách khoá tài khoản sau 5 lần thử sai liên tiếp:**
   Việc khoá tài khoản sau 5 lần sai liên tiếp ngăn chặn hiệu quả tấn công dò thử trực tuyến, nhưng tạo ra **rủi ro tấn công từ chối dịch vụ (Denial of Service — DoS)** nhắm vào người dùng hợp pháp. Kẻ gian chỉ cần biết định danh (`user_id`) của nạn nhân và cố tình gửi 5 yêu cầu xác minh thất bại liên tiếp là có thể vô hiệu hoá hoàn toàn quyền truy cập của nạn nhân vào hệ thống. Để giảm thiểu rủi ro này, thực tế cần kết hợp cơ chế khoá tạm thời theo cấp số nhân (exponential backoff), giới hạn tốc độ theo địa chỉ IP/thiết bị, hoặc yêu cầu xác thực bổ sung qua kênh thứ hai (OTP/Passkey) để mở khoá thay vì khoá cứng vĩnh viễn.

4. **Kịch bản lộ kho mẫu (kèm hoặc không kèm khoá HMAC và token):**
   - **Nếu kho mẫu bị lộ nhưng khoá HMAC và token không lộ:** Kẻ tấn công **không thể** sửa đổi, chèn giả mẫu vào kho (vì không có khoá `TH10_STORE_KEY` để tính lại chữ ký HMAC-SHA256 hợp lệ), và cũng **không thể** khôi phục ảnh khuôn mặt hay vector embedding gốc từ chuỗi 128-bit BioHash vì thiếu ma trận chiếu sinh ra từ token bí mật. Kẻ gian chỉ biết được danh sách `user_id` đã đăng ký.
   - **Nếu cả token cũng bị lộ:** Kẻ tấn công có thể dùng token để sinh lại ma trận chiếu $Q$, từ đó thực hiện tấn công dò tìm nghịch đảo (hill-climbing/pre-image attack) nhằm tái tạo vector đặc trưng gần đúng với mẫu của nạn nhân, hoặc dùng khuôn mặt của chính kẻ tấn công kết hợp token bị lộ để tăng xác suất vượt ngưỡng so khớp (tương ứng mức $\text{EER}_{\text{stolen}} = 7.57\%$).

5. **Ba quyết định thiết kế bảo vệ dữ liệu nhạy cảm theo Luật BVDLCN số 91/2025/QH15 và Nghị định 356/2025/NĐ-CP:**
   Theo Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 và Nghị định 356/2025/NĐ-CP, dữ liệu sinh trắc học là dữ liệu cá nhân nhạy cảm đòi hỏi biện pháp bảo vệ nghiêm ngặt:
   - **Không lưu trữ dữ liệu sinh trắc thô (`BioHashProtector` & `TemplateStore`):** Hệ thống chỉ lưu chuỗi bit đã biến đổi một chiều bằng BioHashing, tuyệt đối không lưu ảnh khuôn mặt hay vector đặc trưng gốc, giúp giảm thiểu thiệt hại và đảm bảo khả năng huỷ bỏ/cấp lại mẫu khi xảy ra sự cố rò rỉ dữ liệu.
   - **Tối thiểu hoá dữ liệu trong nhật ký kiểm toán (`AuditLog`):** Hàm `AuditLog.write` chỉ ghi nhận mã định danh giả, dấu thời gian, trạng thái kết quả và điểm số tổng hợp; nghiêm cấm ghi ảnh, embedding hay chuỗi bit sinh trắc vào tệp log vận hành.
   - **Quy trình ẩn danh hoá và tiêu huỷ dữ liệu sau đánh giá (`pick_people` & Biên bản xoá dữ liệu):** Toàn bộ người dùng trong thử nghiệm được gán mã giả danh (`P01`–`P20`), tách biệt danh tính thật khỏi kho mẫu thử nghiệm, đồng thời thực hiện xoá triệt để tệp kho mẫu, nhật ký và ảnh đầu vào ngay sau khi hoàn tất đánh giá.

## 6. Hạn chế và việc cần làm tiếp

1. **Khả năng chống tấn công phát lại màn hình (`attack_replay`) còn yếu ($\text{APCER} = 44.44\%$):**
   - *Nguyên nhân:* Bộ phân loại PAD tĩnh trên từng khung hình đơn lẻ (MiniFASNet) dễ bị đánh lừa bởi màn hình có độ phân giải cao và tần số quét ổn định.
   - *Việc cần làm tiếp:* Tích hợp cơ chế **thách thức – phản hồi chủ động (Challenge-Response)** ở tầng thu nhận (yêu cầu người dùng quay đầu ngẫu nhiên, chớp mắt hoặc theo dõi chuyển động 3D theo thời gian thực) trước khi đưa khung hình vào PAD tĩnh.
2. **Tỷ lệ không phát hiện được khuôn mặt (FTA) cao khi dùng `opencv` (lên tới `40%` ở kênh replay và `6.67%` ở ảnh thật):**
   - *Nguyên nhân:* Bộ phát hiện Haar Cascade của `opencv` nhạy cảm với góc nghiêng, ánh sáng yếu và nhiễu vân sọc (moiré) từ màn hình, làm tăng tỷ lệ từ chối sai toàn luồng (`FRR = 16.67%`).
   - *Việc cần làm tiếp:* Thay thế `detector_backend="opencv"` bằng các bộ phát hiện dựa trên học sâu như `retinaface` hoặc `mtcnn` để cải thiện độ ổn định phát hiện khuôn mặt.
3. **Thiếu cơ chế chống tấn công chèn dữ liệu (Injection Attack) vào luồng camera:**
   - *Nguyên nhân:* Hàm `DeepFacePad.score` hiện nhận trực tiếp mảng ảnh từ bộ nhớ mà chưa xác thực nguồn gốc phần cứng camera, dễ bị vượt qua nếu máy trạm nhiễm mã độc giả lập camera ảo (tương tự vụ việc tháng 06/2026).
   - *Việc cần làm tiếp:* Bổ sung cơ chế ký số khung hình tại phần cứng cảm biến (Trusted Execution Environment / Camera Signing) và kiểm tra tính toàn vẹn kênh truyền trước khi xử lý PAD.

## 7. Xác nhận xử lý dữ liệu


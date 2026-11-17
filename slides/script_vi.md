# Script thuyết trình tiếng Việt – Slide 11–19 (Đặng Nhật Minh)

Bản tiếng Anh tương ứng nằm trong `presenter_notes.md`. Tổng thời gian khoảng 5 phút 40 giây.

## 11. Learn the load level – or a correction to yesterday (~40s)

Cảm ơn Sơn. Nhóm so sánh 2 baseline theo mùa: lấy tải cùng giờ hôm qua (Naive-24h) hoặc cùng giờ tuần trước (Naive-168h), với 5 model hồi quy: hồi quy tuyến tính, cây quyết định, random forest, SVR kernel RBF và XGBoost. Mỗi model được train theo 2 cách. Bản absolute học trực tiếp mức tải. Bản residual, ký hiệu Delta, học phần chênh so với hôm qua, tức y trừ lag 24, rồi khi dự đoán thì cộng tải hôm qua trở lại. Cả 2 bản đều được tune và so sánh trên cùng một bộ cross-validation.

## 12. Why predict a correction? July tests extrapolation (~40s)

Vì sao lại học phần chênh? Nhìn vào fold 0, tức khoảng validation tháng 7. Tải cao nhất trong tập train khoảng 110.700 kW, nhưng tháng 7 lên tới 133.100, và 12% số giờ tháng 7 cao hơn mọi giá trị model từng thấy. Model dạng cây dự đoán bằng trung bình các giá trị trong train, nên không thể vượt quá mức cao nhất đó. Ngược lại, phần chênh so với hôm qua vẫn nằm trong khoảng quen thuộc: không giờ nào vượt ra ngoài. Sau khi tune, bản residual giảm RMSE tháng 7 của random forest từ 5.554 xuống 3.215 kW, và của XGBoost từ 5.344 xuống 2.979.

## 13. Absolute SVR leads CV, with close alternatives (~55s)

Tiếp theo là tuning. Random search thử 170 bộ tham số cho 5 model, với mỗi loại target, và mỗi bộ được chấm điểm trên cùng 5 fold theo thời gian. Biểu đồ xếp hạng các bản đã tune theo RMSE trung bình CV: SVR absolute đứng đầu với 2.410,6 kW, độ lệch chuẩn khoảng 766. Bảng bên phải cho thấy mức cải thiện so với model mặc định: SVR giảm 39%, cây quyết định 38%, XGBoost và random forest 21 đến 25%, chủ yếu nhờ target residual. Hồi quy tuyến tính gần như không đổi, vì gần như không có gì để tune. Dòng dưới cùng: nếu chỉ dự báo trước 1 giờ, cùng SVR đó giảm còn 1.866 kW, thấp hơn 22,6%, vì nó dùng được tải của vài giờ ngay trước.

## 14. Daily lags drive accuracy; the expanded set hurts (~40s)

Feature nào quan trọng? Ablation này dùng một model duy nhất: **random forest absolute đã tune, giữ nguyên bộ tham số, chạy trên cùng 5 fold CV**. Nhóm thêm từng nhóm feature một. Chỉ có thời tiết thì RMSE là 15.010 kW. Thêm feature lịch giảm khoảng một phần ba, thêm ngày đặc biệt giảm tiếp 9%. Lag theo ngày, tức tải 24 và 48 giờ trước, giảm mạnh nhất, 67%, xuống còn 3.010. Thêm lag tuần và các trung bình trượt thì lại tệ đi, lên 3.700, và XGBoost cũng cho kết quả tương tự. Vì vậy mọi model đều dùng set D, gồm 17 feature.

## 15. The selected SVR halves daily-baseline December RMSE (~35s)

Giờ đến tháng 12, tập test chỉ dùng một lần. SVR được chọn qua CV đạt RMSE 1.624,6 kW: thấp hơn Naive-24h 50,7% và thấp hơn Naive-168h 38%. MAE khoảng 1.095 kW, MAPE 1,78% và R² 0,987. SVR residual ở dưới cùng tình cờ tốt hơn trên tháng 12, 1.419 kW, nhưng nó không phải bản tốt nhất trên CV; nếu đổi sang nó bây giờ thì nghĩa là đang chọn model bằng tập test. Vì vậy SVR absolute vẫn là model cuối cùng.

## 16. Good daily tracking still leaves concentrated errors (~35s)

Hình trên là tải thực tế và dự báo của nhóm cho toàn bộ 720 giờ tháng 12; hai đường gần như trùng nhau. Hình dưới là sai số, bằng dự báo trừ thực tế. Bias tổng thể là −202 kW, tức model dự báo hơi thấp. Sai số tập trung vào một vài thời điểm: ngày tệ nhất là 1/12, lễ Mawlid, một ngày lễ tôn giáo, với MAE 4.579 kW. Ngày lễ rất hiếm trong dữ liệu train, nên vẫn là những ngày khó dự báo nhất.

## 17. Compared with published Tetouan studies (~45s)

So với các bài đã công bố trên cùng bộ dữ liệu thì sao? Đây là con số do từng bài tự báo cáo; nhóm không chạy lại. Islam và Alsalem chỉ dự báo trước 10 phút, và R² của Alsalem chỉ tính cho Zone 3. RoSe không dùng tải quá khứ, nên đó không phải dự báo thật. Biswas báo cáo MAPE 1,04%, nhưng trên trung bình các zone và không nêu tầm dự báo. Bài toán của nhóm là dự báo trước một ngày, model được chọn bằng CV theo thời gian và tháng 12 chỉ dùng một lần, vậy mà vẫn đạt MAPE 1,78% và R² 0,987. Vì target và tầm dự báo khác nhau, bảng này để định vị kết quả của nhóm chứ không để xếp hạng.

## 18. Findings & limitations (~35s)

Ba kết quả chính. Thứ nhất, chọn model cuối bằng CV theo thời gian và báo cáo tháng 12 riêng. Thứ hai, lag theo ngày giúp nhiều nhất, còn feature theo tuần và trung bình trượt làm kết quả tệ hơn. Thứ ba, SVR được chọn giảm một nửa sai số của Naive-24h trong tháng 12, cụ thể là 50,7%. Hạn chế: dữ liệu còn nhỏ, chỉ một năm của một thành phố. Hướng tiếp theo là thu thập thêm nhiều năm dữ liệu.

## 19. Conclusion & Q&A (~15s)

Tóm lại: SVR được chọn qua CV dự báo tháng 12 với RMSE 1.624,6 kW, tốt hơn 50,7% so với việc lấy tải hôm qua. Đây là kết quả khả quan dưới cách đánh giá chặt chẽ theo thời gian. Cảm ơn thầy và các bạn đã lắng nghe, nhóm sẵn sàng nhận câu hỏi.

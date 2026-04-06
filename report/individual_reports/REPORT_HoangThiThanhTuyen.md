# Báo cáo cá nhân: Lab 3 - Chatbot vs ReAct Agent

- **Họ và tên**: Hoàng Thị Thanh Tuyền
- **MSSV**: 2A202600074
- **Ngày**: 06/04/2026

---

## I. Đóng góp kỹ thuật 


- **Module thực hiện**: Tham gia vào việc tích hợp API Từ đồng nghĩa (`src/api/synonym_api.py`).
- **Điểm nổi bật trong mã**:
  - Nghiên cứu và tìm kiếm API cung cấp từ đồng nghĩa miễn phí hoặc phù hợp (lựa chọn Datamuse API).
  - Trực tiếp kiểm thử API (test API) để đảm bảo dữ liệu trả về chính xác, tối ưu thời gian phản hồi trước khi ráp vào hệ thống.
  - Tham gia viết và hoàn thiện code cho module lấy từ đồng nghĩa:
  ```python
  def get_synonyms(word: str) -> List[str]:
      # Datamuse endpoint: rel_syn is used to find synonyms
      api_url = f"https://api.datamuse.com/words?rel_syn={word}"
      try:
          response = requests.get(api_url, timeout=10)
          response.raise_for_status()
          data = response.json()
          synonyms = [item['word'] for item in data]
          return synonyms
      except requests.exceptions.RequestException as e:
          print(f"API connection error: {e}")
          return []
  ```
- **Tài liệu hóa**: Đóng góp chính của tôi tập trung vào khâu đầu vào cho các công cụ của hệ thống. Tôi phụ trách việc nghiên cứu khảo sát các API public, test kỹ tính khả thi của nó, và cùng với nhóm xây dựng nên module `synonym_api`. Việc này giúp trao cho ReAct Agent khả năng đề xuất từ đồng nghĩa thay vì chỉ giới hạn ở việc thêm bớt flashcard cơ bản.

---

## II. Nghiên cứu tình huống lỗi (Debugging Case Study) 

_Phân tích một sự cố cụ thể gặp phải trong quá trình làm lab thông qua hệ thống log._

- **Mô tả vấn đề**: Agent bị vỡ luồng hoặc kẹt trong vòng lặp vô hạn khi tiến hành gọi các công cụ có 0 tham số (ví dụ: `list_flashcard_sets()`) hoặc có nhiều tham số (ví dụ: `add_card_to_set(set_name="School", front="school", back="trường học")`).
- **Nguồn Log**: Trích xuất từ `logs/2026-04-06.log`
  ```text
  Tool execution error: list_sets_func() takes 0 positional arguments but 1 was given
  ...
  Tool execution error: add_card_func() missing 2 required positional arguments: 'front' and 'back'
  ```
- **Chẩn đoán**: Cơ chế dùng biểu thức chính quy (Regex) ở `agent.py` đã gom tất cả tham số truyền vào thành một chuỗi String duy nhất (`action_match.group(2)`). Sau đó hàm `_execute_tool` lại gọi các hàm công cụ một cách thiếu linh hoạt bằng `tool['func'](args)`. Nghĩa là đối với hàm `list_sets_func()`, nó truyền hẳn một chuỗi rỗng `""` (nên bị lỗi vì hàm không yêu cầu tham số). Đối với `add_card_func()`, toàn bộ cụm `set_name="...", front="..."` bị coi là 1 tham số truyền qua `args` thay vì 3 tham số cấu trúc độc lập.
- **Giải pháp**: Logic trích xuất (parsing) tham số ở hàm `_execute_tool` cần xử lý chuẩn chuỗi String thành các argument. Khuyến nghị yêu cầu LLM xuất params dưới dạng JSON chuẩn, parse bằng `json.loads(args)` rồi chèn vào bằng `tool['func'](**parsed_args)`. Cách khác là thay đổi các hàm khai báo trong `tools.py` để tất cả đều chỉ nhận vào đúng một đối số chuỗi String và tự thân chúng sẽ parse giá trị theo yêu cầu.

---

## III. Cảm nhận cá nhân: Chatbot vs ReAct Agent 

_Đánh giá sự khác biệt về năng lực suy luận._

1. **Suy luận (Reasoning)**: Khối `Thought` buộc Agent (tác nhân) chia nhỏ bài toán trước khi hành động. Trong lab, khi được yêu cầu tạo một flashcard, Agent thiết lập chiến lược: (1) Kiểm tra xem bộ này tồn tại chưa -> (2) Xem các card bên trong -> (3) Thêm thẻ mới. Một chatbot bình thường sẽ chỉ sinh ngay ra nội dung nháp bỏ qua trạng thái thực của ứng dụng.
2. **Độ tin cậy (Reliability)**: Ở những tình huống trao đổi hay hỏi định nghĩa đơn giản (ví dụ: "nghĩa của từ hoa là gì"), ReAct Agent đôi khi làm phức tạp hóa vấn đề do bị tốn thời gian gọi tool, sinh ra độ trễ (latency). Hoặc nếu xuất hiện lỗi format lúc gọi tool thì sẽ rất dễ mắc kẹt trong vòng lặp thử đi thử lại lỗi sai cũ, khuyết điểm này Chatbot thường không gặp phải vì nó chỉ tư duy hội thoại suông tĩnh.
3. **Quan sát (Observation)**: Observation đóng vai trò ghim thực tế cho Agent. Trong log của phiên chạy, khi tác nhân cố gọi hàm sinh template lỗi (`Error: Card set already exists...`), nhờ đọc được quan sát này, LLM ngay lập tức lật sang phương án kiểm tra tiếp nội dung của bộ flashcard (`list_cards_in_set`) thay vì vẫn bướng bỉnh thử ghi đè hoài.

---

## IV. Định hướng cải tiến cho tương lai 

_Làm thế nào để mở rộng năng lực Agent thành một hệ thống AI mức Production._

- **Khả năng tự chủ (Scalability)**: Nâng cấp hẳn từ Regex thô sang JSON-based (giống OpenAI Function Calling API). Tránh tối đa các lỗi thiếu key-value arguments, nhất là trong bối cảnh tương lai ReAct tích hợp thêm hàng chục API phức tạp nữa.
- **Tính an toàn (Safety)**: Viết thêm cơ chế kiểm soát retry limit đứt dòng. Không cho phép Agent suy nghĩ dông dài về một lỗi `TypeError` lặp lại, nếu gọi sai tool 2-3 lần liên tiếp, hệ thống nên tự bypass báo cáo lỗi ra màn hình cho End-user khắc phục.
- **Hiệu năng (Performance)**: Tạo lớp bộ nhớ đệm (Cache) cho các đầu API ngoại vi (Oxford và Synonym Datamuse). Do học thuật hay trùng lặp từ vựng cơ bản, Caching sẽ làm giảm tối đa chi phí gọi API và thời gian đợi từ mạng cho Agent.

---

> [!NOTE]
> Báo cáo của Hoàng Thị Thanh Tuyền

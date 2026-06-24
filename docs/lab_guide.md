# Lab Guide: Multi-Agent Research System

## Scenario

Bạn cần xây dựng một research assistant có thể nhận câu hỏi dài, tìm thông tin, phân tích và viết câu trả lời cuối cùng. Lab yêu cầu so sánh hai cách làm:

1. **Single-agent baseline**: một agent làm toàn bộ.
2. **Multi-agent workflow**: Supervisor điều phối Researcher, Analyst, Writer.

## Quy tắc quan trọng

- Không thêm agent nếu không có lý do rõ ràng.
- Mỗi agent phải có responsibility riêng.
- Shared state phải đủ rõ để debug.
- Phải có trace hoặc log cho từng bước.
- Phải benchmark, không chỉ nhìn output bằng cảm tính.

## Milestone 1: Baseline

File gợi ý:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

TODO(student): thay baseline placeholder bằng một call LLM thật.

## Milestone 2: Supervisor

File gợi ý:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

TODO(student): implement routing policy.

Gợi ý câu hỏi thiết kế:

- Khi nào gọi Researcher?
- Khi nào gọi Analyst?
- Khi nào gọi Writer?
- Khi nào stop?
- Nếu agent fail thì retry hay fallback?

## Milestone 3: Worker agents

File gợi ý:

- `agents/researcher.py`
- `agents/analyst.py`
- `agents/writer.py`

TODO(student): implement từng worker.

## Milestone 4: Trace và benchmark

File gợi ý:

- `observability/tracing.py`
- `evaluation/benchmark.py`
- `evaluation/report.py`

Benchmark tối thiểu:

| Metric | Cách đo gợi ý |
|---|---|
| Latency | wall-clock time |
| Cost | token usage hoặc provider usage |
| Quality | rubric 0-10 do peer review |
| Citation coverage | số claims có source / tổng claims chính |
| Failure rate | số query fail / tổng query |

## Exit ticket

Mỗi nhóm trả lời 2 câu:

1. **Case nào nên dùng multi-agent? Vì sao?**
   - **Nên dùng:** Các tác vụ nghiên cứu học thuật sâu rộng, phát triển phần mềm phức tạp, lập kế hoạch thực nghiệm, hoặc viết báo cáo đa chiều.
   - **Lý do:** Những bài toán này đòi hỏi sự phối hợp của nhiều kỹ năng chuyên biệt (tìm kiếm nguồn tin cậy, phân tích phản biện, tổng hợp văn bản). Multi-Agent phân tách rõ ràng ngữ cảnh và nhiệm vụ của từng agent, tránh được việc LLM bị quá tải thông tin, giảm thiểu tối đa ảo giác (hallucination) qua cơ chế kiểm chứng chéo và phản biện nội bộ.

2. **Case nào không nên dùng multi-agent? Vì sao?**
   - **Không nên dùng:** Các tác vụ giao dịch trực tiếp, đơn giản và có tính chất tuyến tính (như dịch câu ngắn, phân loại văn bản đơn giản, chatbot hỏi đáp FAQ cơ bản).
   - **Lý do:** Việc sử dụng Multi-Agent trong các tình huống này sẽ làm tăng độ trễ (latency) và chi phí token vô ích, trong khi không đem lại sự khác biệt đáng kể nào về chất lượng đầu ra so với một lượt gọi LLM đơn lẻ (Single-Call).


// Vercel 서버리스 함수: AI 채팅 → OpenAI GPT-4o-mini 연동
// 환경변수 GPT_API_KEY 필요 (Vercel 프로젝트 환경변수에 설정)

const SYSTEM_PROMPT = `너는 한국지역난방공사(KDHC) 설비 운영·관리 담당자를 돕는 데이터 도우미다.
아래 [운영 데이터]를 근거로 한국어로 친절하고 간결하게 답한다.
핵심 수치는 필요하면 표(마크다운)나 목록으로 정리한다.
[운영 데이터]에 없는 값은 추측하지 말고 "현재 제공된 데이터에 없다"고 답한다.

[운영 데이터 — 2024년 10월 기준]
- 누적 열 생산량: 12,450 Gcal (전일 대비 +2.4%)
- 발전 실적: 8,920 MWh (전일 대비 -1.1%)
- LNG 사용량: 4,105 Ton (변동 없음)
- 설비 상태: 터빈 A 정상 / 보일러 1 정상 / 펌프 C 점검요망(경고)
- 총 열판매량: 1,452,030 Gcal (전월 대비 +4.2%, 전년동월 대비 +2.1%)
- 총 전기판매량: 892,105 MWh (전월 대비 -1.5%)
- 지사별 열판매량(Gcal): 강남 315,050(+2.1%) / 판교 280,100(+5.4%) / 파주 205,800(0.0%) / 수원 248,000(+1.8%)
- 지사별 전기판매량(MWh): 강남 148,900(-0.5%) / 판교 118,500(+1.2%) / 파주 93,200(-3.1%) / 수원 108,100(+0.8%)
- 현재 기상(성남시, 12:00): 기온 14.2°C, 습도 45%, 풍속 3.5 m/s(북서풍)
- 예상 시간당 열수요: 842 Gcal/h (수요 증가 추세)
- 연료 재고: LNG 12,300T(충분) / 유연탄 5,400T(충분) / 바이오매스 1,150T(주의) / 경유 880T(충분)
- 평균 열효율: 91.4% (최적 구간)`;

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "POST 요청만 허용됩니다." });
    return;
  }

  const apiKey = process.env.GPT_API_KEY;
  if (!apiKey) {
    res.status(500).json({ error: "서버에 GPT_API_KEY가 설정되지 않았습니다." });
    return;
  }

  let body = req.body;
  if (typeof body === "string") {
    try { body = JSON.parse(body); } catch { body = {}; }
  }
  body = body || {};

  const history = Array.isArray(body.messages) ? body.messages : null;
  const single = typeof body.message === "string" ? body.message.trim() : "";

  const chat = [{ role: "system", content: SYSTEM_PROMPT }];
  if (history && history.length) {
    chat.push(...history.filter(m => m && m.role && m.content));
  } else if (single) {
    chat.push({ role: "user", content: single });
  } else {
    res.status(400).json({ error: "message 또는 messages가 필요합니다." });
    return;
  }

  try {
    const r = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: chat,
        temperature: 0.2,
      }),
    });
    const data = await r.json();
    if (!r.ok) {
      res.status(502).json({ error: data?.error?.message || "OpenAI 호출 실패" });
      return;
    }
    const reply = data?.choices?.[0]?.message?.content || "(빈 응답)";
    res.status(200).json({ reply });
  } catch (e) {
    res.status(502).json({ error: "OpenAI 호출 중 오류: " + String(e?.message || e) });
  }
}

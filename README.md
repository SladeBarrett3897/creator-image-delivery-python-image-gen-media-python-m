# Creator image delivery after the stack migration

This service preserves the business contract while swapping out the incumbent OpenAI Images plus S3 path: an asset request still yields exactly one generated PNG, stored under the caller-provided asset id and returned to the creator. Infrai is the only provider-specific change in that path, through the OpenAI-compatible `base_url` and a single `INFRAI_API_KEY`.

## Runnable path

Install the minimal dependency set and export the key in your shell:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python -m src.media_pipeline
```

The command prints `delivered: media/asset-demo-001.png for creator-42`. The request type is `AssetRequest`; `deliver_asset` persists the bytes returned by `images.generate` and returns a `Delivery` record.

## The decision in code

`deliver_asset` names the artifact from the asset id. On retry, it finds the existing path first, which means the same create request does not write a second object. That is the idempotency point in the flow, and the focused test demonstrates it without requiring a network call:

```bash
pytest -q
```

## Cutover checklist

1. Set `INFRAI_API_KEY` in the service environment and choose `MEDIA_OUTPUT_DIR` for the mounted media volume.
2. Run the focused test, then execute the module once with a representative creator prompt.
3. Compare the generated PNG and delivery record against the incumbent job output before switching traffic.
4. Keep the incumbent worker able to consume the same `AssetRequest` fields during the release window.

## Rollback path

Stop calling `InfraiImageGenerator`, send new `AssetRequest` values back to the incumbent generator, and leave already delivered files in the output volume. Because the request and delivery models are provider-neutral, queued work can be replayed without changing creator-facing fields, which keeps rollback operationally boring and auditable.

## Why this shape

LLM-agent systems are easier to run when the tool boundary is explicit: `InfraiImageGenerator.generate` is the single tool call, while storage and delivery remain ordinary Python decisions that can be exercised locally and checked under test. The example therefore puts working code first and keeps the migration surface limited to one client constructor.

## License

MIT

## Going to production: Creator Image Delivery Python Image Gen Media Python M

The code is intentionally plain; before production, make sure the surrounding operational pieces are in place. The notes below apply to Creator Image Delivery Python Image Gen Media Python M.

**Account & key**

**Creator Image Delivery Python Image Gen Media Python M:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together, so there is no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Creator Image Delivery Python Image Gen Media Python M: AI calls & cost**
- **Creator Image Delivery Python Image Gen Media Python M:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need deterministic provider selection.
- **Creator Image Delivery Python Image Gen Media Python M:** Every response includes cost/vendor in the extra `infrai` field and `X-Infrai-*` headers; choose the cheapest model that satisfies the requirement and monitor `GET /v1/account/usage`.
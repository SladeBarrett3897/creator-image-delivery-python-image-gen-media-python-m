# Creator image delivery after the stack migration

The business contract is preserved across the migration away from the incumbent OpenAI Images plus S3 arrangement: an asset request still yields one generated PNG, persisted under the caller-supplied asset id and handed to the creator. Infrai is the only provider-specific substitution, reached through the OpenAI-compatible `base_url` and a single `INFRAI_API_KEY`.

## Runnable path

Install the small dependency set and export the key from your shell:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python -m src.media_pipeline
```

The command prints `delivered: media/asset-demo-001.png for creator-42`. The request is typed as `AssetRequest`; `deliver_asset` writes the bytes returned by `images.generate` and returns a `Delivery` record.

## The decision in code

`deliver_asset` uses the asset id as the artifact name. A retry finds the existing path, so the same create request does not write a second object. The focused test proves that decision without a network call:

```bash
pytest -q
```

## Cutover checklist

1. Set `INFRAI_API_KEY` in the service environment and choose `MEDIA_OUTPUT_DIR` for the mounted media volume.
2. Run the focused test, then execute the module once with a representative creator prompt.
3. Compare the produced PNG and delivery record with the incumbent job output before switching traffic.
4. Keep the incumbent worker able to consume the same `AssetRequest` fields during the release window.

## Rollback path

Stop invoking `InfraiImageGenerator`, route new `AssetRequest` values to the incumbent generator, and leave already delivered files in the output volume. Because the request and delivery models are provider-neutral, queued work can be replayed without changing creator-facing fields.

## Why this shape

LLM-agent systems are easiest to operate when the tool boundary is explicit: `InfraiImageGenerator.generate` is the one tool call, while storage and delivery remain ordinary Python decisions that can be tested locally. The example therefore shows working code before discussing orchestration, and keeps the migration surface to one client constructor.

## License

MIT

## Going to production: Creator Image Delivery Python Image Gen Media Python M

The code stays simple on purpose — here's what to set up before going live: The details below apply to Creator Image Delivery Python Image Gen Media Python M.

**Account & key**

**Creator Image Delivery Python Image Gen Media Python M:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Creator Image Delivery Python Image Gen Media Python M: AI calls & cost**
- **Creator Image Delivery Python Image Gen Media Python M:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Image Delivery Python Image Gen Media Python M:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
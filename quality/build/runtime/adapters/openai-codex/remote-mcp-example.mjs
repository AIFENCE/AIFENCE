// Illustrative OpenAI Responses API configuration. Provide your own HTTPS MCP URL and auth policy.
import OpenAI from 'openai';
const client=new OpenAI();
const response=await client.responses.create({model:process.env.OPENAI_MODEL||'YOUR_MODEL',input:'Use BizIQ to plan a production dashboard.',tools:[{type:'mcp',server_label:'biziq',server_url:process.env.BIZIQ_MCP_URL,allowed_tools:['biziq_initialize','biziq_plan','biziq_get_sections','biziq_get_control','biziq_get_artifact_contract','biziq_validate']} ]});
console.log(response.output_text);

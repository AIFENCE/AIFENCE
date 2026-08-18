// Illustrative OpenAI Responses API configuration. Provide your own HTTPS MCP URL and auth policy.
import OpenAI from 'openai';
const client=new OpenAI();
const response=await client.responses.create({model:process.env.OPENAI_MODEL||'YOUR_MODEL',input:'Use AIFENCE to plan a production dashboard.',tools:[{type:'mcp',server_label:'aifence',server_url:process.env.AIFENCE_MCP_URL,allowed_tools:['aifence_quality_initialize','aifence_quality_plan','aifence_quality_get_sections','aifence_quality_get_control','aifence_quality_get_artifact_contract','aifence_quality_validate']} ]});
console.log(response.output_text);

using Azure.AI.OpenAI;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Options;

namespace SampleDotNetApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class HelloController : ControllerBase
{
    private readonly OpenAIClient _client;
    private readonly OpenAIOptions _options;

    public HelloController(OpenAIClient client, IOptions<OpenAIOptions> options)
    {
        _client = client;
        _options = options.Value;
    }

    [HttpPost]
    public async Task<IActionResult> Post([FromBody] ChatRequest request)
    {
        var chatOptions = new ChatCompletionsOptions()
        {
            Messages =
            {
                new ChatMessage(ChatRole.User, request.Input)
            }
        };

        var response = await _client.GetChatCompletionsAsync(
            deploymentOrModelName: _options.DeploymentName,
            chatOptions);

        var message = response.Value.Choices.First().Message.Content;
        return Ok(new { response = message });
    }

    public class ChatRequest
    {
        public string Input { get; set; }
    }
}

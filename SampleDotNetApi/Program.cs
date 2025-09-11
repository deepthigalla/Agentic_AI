using Azure;
using Azure.AI.OpenAI;

var builder = WebApplication.CreateBuilder(args);

// Register OpenAI settings
builder.Services.Configure<OpenAIOptions>(
    builder.Configuration.GetSection("AzureOpenAI"));

// Register OpenAI client as a singleton
builder.Services.AddSingleton(sp =>
{
    var config = sp.GetRequiredService<IConfiguration>();
    var endpoint = new Uri(config["AzureOpenAI:Endpoint"]);
    var key = new AzureKeyCredential(config["AzureOpenAI:ApiKey"]);
    return new OpenAIClient(endpoint, key);
});

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();
app.Run();

// Options class to bind configuration
public class OpenAIOptions
{
    public string Endpoint { get; set; }
    public string ApiKey { get; set; }
    public string DeploymentName { get; set; }
    public string ApiVersion { get; set; }
}

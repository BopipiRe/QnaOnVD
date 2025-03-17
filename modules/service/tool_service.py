import requests
from langchain.agents import Tool, initialize_agent
from langchain.llms import Ollama

# 配置高德天气API（需提前申请key）
API_KEY = "your_gaode_key"
CITY_CODE_URL = "https://restapi.amap.com/v3/config/district?keywords={city}&subdistrict=0&key={key}"


def get_city_code(city: str) -> str:
    """获取城市行政区编码"""
    response = requests.get(CITY_CODE_URL.format(city=city, key=API_KEY)).json()
    return response['districts'][0]['adcode']


def weather_query(city: str, date: str = None) -> dict:
    """天气查询工具实现"""
    city_code = get_city_code(city)
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?key={API_KEY}&city={city_code}&extensions=all"
    response = requests.get(url).json()

    # 提取指定日期数据（默认当天）
    forecast = next(
        (item for item in response['forecasts'][0]['casts']
         if item['date'] == (date or response['reporttime'][:10])),
        None
    )
    return {
        "temperature": forecast['daytemp'],
        "humidity": forecast['nighttemp'],
        "weather": forecast['dayweather']
    }


# 初始化大模型
llm = Ollama(model="qwen2.5:1.5b", temperature=0.3)

# 注册工具集
tools = [
    Tool(
        name="WeatherQuery",
        func=weather_query,
        description="调用天气API获取指定城市的气温、湿度等信息，参数格式：{'city': 城市名称, 'date': 日期（可选）}"
    )
]

# 配置对话记忆
# memory = ConversationBufferMemory(memory_key="chat_history")

# 创建代理
agent = initialize_agent(
    tools,
    llm,
    agent="conversational-react-description",
    # memory=memory,
    verbose=True
)

# 对话测试
if __name__ == "__main__":
    while True:
        query = input("用户：")
        if query.lower() in ['exit', 'quit']: break
        response = agent.run(query)
        print(f"AI：{response}")
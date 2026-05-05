import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.tools import tool
from tavily import TavilyClient
import requests
from bs4 import BeautifulSoup
from rich import print





tavily = TavilyClient(api_key="tvly-dev-xxx")  # add your api key


@tool
def search_tool(querys:str)->str:
    """This tool is used for searching , fetching live data , current data and latest information """
    results= tavily.search(query=querys,max_results=5)
    out=[]
    for r in results['results']:
       out.append(
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
       )
    return "\n----\n".join(out)
@tool
def scrap_text(url:str)->str:
    """Scrap and give clean text from the given url for deep reading"""
    try:
        response= requests.get(url,timeout=8,headers={"User-Agent":'Mozilla/5.0'})
        soup= BeautifulSoup(response.text,"html.parser")
        for tag in soup(["script","style","nav","footer"]):
            tag.decompose()
        return soup.get_text(separator=" ",strip=True)[:3000]
    except Exception as e:
        return f"Cound not scrap URL:{str(e)}"


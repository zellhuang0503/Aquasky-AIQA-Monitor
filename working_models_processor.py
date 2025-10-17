#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AQUASKY AIQA Monitor - 撌脤?霅?冽芋???
撠釣?澆歇?亙?函?璅∪?嚗??其??舐?芋??
"""

import os
import sys
import json
import requests
import configparser
import time
from datetime import datetime
from pathlib import Path
import pandas as pd

class WorkingModelsProcessor:
    """撌脤?霅?冽芋??????""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.output_dir = self.project_root / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        # 撌脤?霅?函?璅∪?嚗??園?瘙矽?湛?
        self.working_models = [
            # 撌脫??葫閰阡??芋??            {
                "id": "deepseek/deepseek-chat-v3.1",
                "name": "DeepSeek Chat v3.1",
                "status": "verified"  # 撌脫??            },
            {
                "id": "openai/gpt-5-mini",
                "name": "GPT-5 Mini",
                "status": "verified"   # 撌脤?霅??            },
            # 雿輻??瘙宏??Claude 3 Haiku
            {
                "id": "google/gemini-2.5-flash",
                "name": "Gemini 2.5 Flash",
                "status": "verified"   # 撌脤?霅??            },
            # ?嗅?撌脤?霅?函?璅∪?
            {
                "id": "anthropic/claude-sonnet-4",
                "name": "Claude Sonnet 4",
                "status": "verified"   # 撌脤?霅??            },
            {
                "id": "meta-llama/llama-3.1-8b-instruct",
                "name": "Llama 3.1 8B",
                "status": "verified"   # 撌脤?霅??            },
            {
                "id": "mistralai/mistral-small-3.2-24b-instruct",
                "name": "Mistral Small 3.2 24B",
                "status": "verified"   # 撌脫??            },
            # 雿輻??摰????Perplexity 璅∪?嚗歇撽??舐嚗?            {
                "id": "perplexity/sonar-pro",
                "name": "Perplexity Sonar Pro",
                "status": "verified",   # 撌脤?霅??                "api_type": "perplexity"  # 雿輻 Perplexity ?湔 API
            },
            # OpenRouter ?舐??Grok 璅∪?嚗歇皜祈岫 2025-07-26嚗?            {
                "id": "x-ai/grok-3-mini-beta",
                "name": "Grok 3 Mini Beta",
                "status": "verified"   # 撌脤?霅?剁?2.74蝘????敹恬?
            },
            # 銝?函?璅∪?嚗????箄???
            # {
            #     "id": "x-ai/grok-beta",
            #     "name": "Grok Beta",
            #     "status": "unavailable"   # HTTP 404 - No endpoints found
            # }
        ]

        # ?岫敺???JSON 閬?璅∪?皜嚗摮銝撘迤蝣綽?
        try:
            config_json = self.project_root / 'config' / 'working_models.json'
            if config_json.exists():
                with open(config_json, 'r', encoding='utf-8') as f:
                    models = json.load(f)
                if isinstance(models, list) and all(isinstance(m, dict) and 'id' in m and 'name' in m for m in models):
                    self.working_models = models
                    print(f"撌脰??亙??冽芋???殷?{config_json}")
                else:
                    print("憭璅∪?皜?澆?銝迤蝣綽??寧?批遣皜??)
        except Exception as e:
            print(f"霈???冽芋???桀仃???寧?批遣皜嚗e}")

        self.openrouter_api_key = None
        self.perplexity_api_key = None
        self.questions = []
        
    def load_config(self):
        """頛?蔭瑼?"""
        print("\n ??頛?蔭瑼?...")
        config = configparser.ConfigParser()
        config_path = Path("config.ini")
        
        if not config_path.exists():
            print("?曆???config.ini 瑼?")
            return False
        
        config.read(config_path, encoding='utf-8')
        
        # 頛 OpenRouter API Key
        self.openrouter_api_key = config.get('api_keys', 'openrouter_api_key', fallback=None)
        
        # 頛 Perplexity API Key
        self.perplexity_api_key = config.get('api_keys', 'PERPLEXITY_API_KEY', fallback=None)
        
        if not self.openrouter_api_key or self.openrouter_api_key == 'your_openrouter_api_key_here':
            print("隢 config.ini 銝剛身摰??? openrouter_api_key")
            return False
        
        if not self.perplexity_api_key or self.perplexity_api_key == 'your_perplexity_api_key_here':
            print("隢 config.ini 銝剛身摰??? PERPLEXITY_API_KEY")
            return False
        
        return True
    
    def extract_questions(self):
        """敺?憿?獢葉?????20 ??憿?""
        print("\n ??????...")
        candidates = [\n            Path("AQUASKY AEO 監控專案 - 黃金問題庫 V3.0.md"),\n            Path("AQUASKY AEO 監控專案 - 黃金問題庫 V3.0_processed.md"),\n        ]\n        questions_file = next((p for p in candidates if p.exists()), None)
        
        if not questions_file:\n            print("找不到題庫檔案（V3.0.md 或 V3.0_processed.md）")\n            return False
        
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            questions = []
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, 13)):
                    question = line.split('.', 1)[1].strip()
                    if '(' in question and ')' in question:
                        question = question.split('(')[0].strip()
                    questions.append(question)
            
            self.questions = questions[:12]
            print(f"???? {len(questions)} ??憿?)
            return len(questions) > 0
            
        except Exception as e:
            print(f"霈??憿?獢??潛??航炊: {str(e)}")
            return False
    
    def test_model_availability(self, model_info):
        """皜祈岫璅∪??臬?舐嚗??OpenRouter ??Perplexity嚗?""
        model_id = model_info["id"]
        api_type = model_info.get("api_type", "openrouter")
        
        print(f"\n 皜祈岫璅∪? {model_id} ?臬?舐...")
        
        if api_type == "perplexity":
            # 雿輻 Perplexity ?湔 API
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            actual_model_id = model_id.replace("perplexity/", "")
        else:
            # 雿輻 OpenRouter API
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/zellhuang0503/Aquasky-AIQA-Monitor",
                "X-Title": "AQUASKY AIQA Monitor"
            }
            actual_model_id = model_id
        
        # 雿輻蝪∪?葫閰血?憿?        data = {
            "model": actual_model_id,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, please respond with 'OK' if you can understand this message."
                }
            ],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        try:
            print(f"  皜祈岫璅∪??舐??..")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    print(f"  璅∪??舐")
                    return True
                else:
                    print(f"  璅∪????澆??啣虜")
                    return False
            else:
                print(f"  璅∪?銝??(HTTP {response.status_code})")
                try:
                    error_info = response.json()
                    print(f"      ?航炊閰單?: {error_info}")
                except:
                    print(f"      ?航炊?批捆: {response.text}")
                return False
                
        except Exception as e:
            print(f"  皜祈岫璅∪???隤? {str(e)}")
            return False
    
    def call_llm_api(self, model_info, question, question_num):
        """?澆 LLM API嚗??OpenRouter ??Perplexity嚗?""
        model_id = model_info["id"]
        api_type = model_info.get("api_type", "openrouter")
        
        if api_type == "perplexity":
            # 雿輻 Perplexity ?湔 API
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            # Perplexity 璅∪? ID ?閬宏??perplexity/ ?韌
            actual_model_id = model_id.replace("perplexity/", "")
        else:
            # 雿輻 OpenRouter API
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/zellhuang0503/Aquasky-AIQA-Monitor",
                "X-Title": "AQUASKY AIQA Monitor"
            }
            actual_model_id = model_id
        
        data = {
            "model": actual_model_id,
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            print(f"  ???? {question_num}/20...")
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    answer = result['choices'][0]['message']['content']
                    usage = result.get('usage', {})
                    
                    print(f"  ?? {question_num} 摰? (Token: {usage.get('total_tokens', 0)})")
                    return {
                        'success': True,
                        'answer': answer,
                        'usage': usage
                    }
                else:
                    print(f"  ?? {question_num} - API ???澆??啣虜")
                    return {'success': False, 'error': 'Invalid response format'}
            else:
                print(f"  ?? {question_num} - API ?航炊: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                    
        except Exception as e:
            print(f"  ?? {question_num} - ?潛??航炊: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_single_model(self, model_info):
        """???桐?璅∪?????憿?""
        model_id = model_info["id"]
        model_name = model_info["name"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"\n ????璅∪?: {model_name} ({model_id})")
        
        print(f"\n ????璅∪?: {model_name}")
        print(f" 璅∪?ID: {model_id}")
        print("=" * 60)
        
        # 憒?銝撌脤?霅?璅∪?嚗?皜祈岫?舐??        if model_info["status"] != "verified":
            if not self.test_model_availability(model_info):
                print(f"璅∪? {model_name} 銝?剁?頝喲???")
                return False, 0, 0
        
        results = []
        successful_count = 0
        total_tokens = 0
        
        for i, question in enumerate(self.questions, 1):
            result = self.call_llm_api(model_info, question, i)
            results.append(result)
            
            if result['success']:
                successful_count += 1
                total_tokens += result.get('usage', {}).get('total_tokens', 0)
            
            # 瘥?憿????3 蝘?            if i < len(self.questions):
                time.sleep(3)
        
        # ?脣?蝯?
        self.save_model_results(model_id, model_name, results, timestamp)
        
        print(f"\n {model_name} ??摰?:")
        print(f"  ??: {successful_count}/20 ??憿?)
        print(f"  蝮確oken: {total_tokens}")
        print("=" * 60)
        
        return True, successful_count, total_tokens
    
    def save_model_results(self, model_id, model_name, results, timestamp):
        """?脣??桐?璅∪?????""
        # 皞?鞈?
        data = []
        
        for i, (question, result) in enumerate(zip(self.questions, results), 1):
            row = {
                '??蝺刻?': i,
                '??': question,
                '??': result.get('answer', '??憭望?') if result['success'] else '??憭望?',
                '???: '??' if result['success'] else '憭望?',
                '?航炊閮': result.get('error', '') if not result['success'] else '',
                '頛詨Token': result.get('usage', {}).get('prompt_tokens', 0) if result['success'] else 0,
                '頛詨Token': result.get('usage', {}).get('completion_tokens', 0) if result['success'] else 0,
                '蝮確oken': result.get('usage', {}).get('total_tokens', 0) if result['success'] else 0
            }
            data.append(row)
        
        # ??摰??獢?蝔?        safe_model_name = model_id.replace('/', '_').replace('\\', '_')
        
        # ?脣? Excel
        df = pd.DataFrame(data)
        excel_filename = f"AQUASKY_AIQA_{safe_model_name}_{timestamp}.xlsx"
        excel_path = self.output_dir / excel_filename
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        # ?脣? Markdown
        md_filename = f"AQUASKY_AIQA_{safe_model_name}_{timestamp}.md"
        md_path = self.output_dir / md_filename
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# AQUASKY AIQA Monitor - {model_name} 皜祈岫?勗?\n\n")
            f.write(f"**????**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**璅∪?**: {model_id}\n")
            f.write(f"**璅∪??迂**: {model_name}\n\n")
            
            # 蝯梯?鞈?
            successful_count = sum(1 for r in results if r['success'])
            total_input_tokens = sum(r.get('usage', {}).get('prompt_tokens', 0) for r in results if r['success'])
            total_output_tokens = sum(r.get('usage', {}).get('completion_tokens', 0) for r in results if r['success'])
            
            f.write(f"## 蝯梯?鞈?\n\n")
            f.write(f"- **??????*: {successful_count}/20\n")
            f.write(f"- **蝮質撓?冉oken**: {total_input_tokens}\n")
            f.write(f"- **蝮質撓?摭oken**: {total_output_tokens}\n")
            f.write(f"- **蝮確oken**: {total_input_tokens + total_output_tokens}\n\n")
            
            # ????蝑?            for i, (question, result) in enumerate(zip(self.questions, results), 1):
                f.write(f"## ?? {i}\n\n")
                f.write(f"**??**: {question}\n\n")
                if result['success']:
                    f.write(f"**??**: {result['answer']}\n\n")
                    usage = result.get('usage', {})
                    f.write(f"**Token雿輻**: 頛詨 {usage.get('prompt_tokens', 0)}, 頛詨 {usage.get('completion_tokens', 0)}, 蝮質? {usage.get('total_tokens', 0)}\n\n")
                else:
                    f.write(f"**???*: ??憭望?\n")
                    f.write(f"**?航炊**: {result.get('error', '?芰?航炊')}\n\n")
                f.write("---\n\n")
        
        print(f"  蝯?撌脣摮?")
        print(f"    Excel: {excel_filename}")
        print(f"    Markdown: {md_filename}")
    
    def run_processing(self):
        """?瑁???"""
        print("AQUASKY AIQA Monitor - ?舐璅∪???蝟餌絞")
        print("=" * 60)
        
        # 頛?蔭
        if not self.load_config():
            return False
        
        # ????
        if not self.extract_questions():
            return False
        
        print(f"\n 撠?摨??誑銝芋??")
        for i, model in enumerate(self.working_models, 1):
            status_icon = "[V]" if model["status"] == "verified" else "[T]"
            print(f"  {i}. {status_icon} {model['name']} ({model['id']})")
        
        print(f"\n 瘥芋???? 20 ??憿?摰?敺?摮???)
        print("=" * 60)
        
        # ????瘥芋??        total_successful = 0
        total_tokens = 0
        processed_models = 0
        
        for i, model_info in enumerate(self.working_models, 1):
            print(f"\n ?脣漲: {i}/{len(self.working_models)}")
            
            try:
                success, successful, tokens = self.process_single_model(model_info)
                
                if success:
                    processed_models += 1
                    total_successful += successful
                    total_tokens += tokens
                
                # 璅∪?銋??怠? 5 蝘?                if i < len(self.working_models):
                    print(f"?怠? 5 蝘???銝??芋??..")
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                print(f"\n 雿輻?葉?瑁???撌脣???{processed_models} ?芋??)
                break
            except Exception as e:
                print(f"\n ??璅∪? {model_info['name']} ??隤? {str(e)}")
                continue
        
        # 憿舐內蝮賜?
        print(f"\n ??摰?嚗?)
        print(f" ????璅∪??? {processed_models}")
        print(f" 蝮賣???憿: {total_successful}")
        print(f" 蝮確oken雿輻: {total_tokens}")
        print(f" ?????獢歇?脣???outputs/ ?桅?")
        print("=" * 60)
        
        return True

def main():
    """銝餌?撘?""
    print("===== ???瑁? working_models_processor.py =====")
    try:
        processor = WorkingModelsProcessor()
        processor.run_processing()
    except Exception as e:
        import traceback
        print(f"\n ?潛??芣??脩??航炊: {str(e)}")
        print("閰喟敦?航炊餈質馱:")
        traceback.print_exc()
    print("===== ?單?瑁?蝯? ====")

if __name__ == "__main__":
    main()


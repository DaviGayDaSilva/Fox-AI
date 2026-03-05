"""
Fox-AI - Assistente Virtual Amigável
Um assistente de IA gentil, respeitoso e prestativo para o Firefox
Powered by TinyLlama 1.1B
"""

from flask import Flask, render_template, request, jsonify
import random
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__, template_folder='templates')

# Flag para controlar uso do modelo de IA
USE_LLM = True

# Carregar modelo TinyLlama
print("🤖 Carregando TinyLlama 1.1B... (pode levar alguns minutos na primeira vez)")
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="float16",
        device_map="auto",
        low_cpu_mem_usage=True
    )
    
    # Criar pipeline de texto
    llm_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=150,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )
    print("✅ TinyLlama carregado com sucesso!")
    USE_LLM = True
except Exception as e:
    print(f"⚠️ Erro ao carregar TinyLlama: {e}")
    print("📝 Usando modo offline (respostas predefinidas)")
    USE_LLM = False
    llm_pipeline = None

# Respostas amigáveis e respetuosas do assistente
class FoxAssistant:
    def __init__(self):
        self.name = "Fox"
        self.greetings = [
            "Olá! Que bom ter você por aqui! 😊",
            "Oi! Estou tão feliz em te ver! 🦊",
            "Olá! Como posso te ajudar hoje?",
            "Hey! Bem-vindo de volta! ✨",
            "Oi! É um prazer te encontrar! 🌟"
        ]
        
        self.responses = {
            'greeting': [
                "Olá! Que prazer te ver! Sou o Fox, seu assistente. Como posso ajudar hoje?",
                "Oi! Estou aqui para ajudar no que precisar! 😊",
                "Olá! Que bom ter você aqui! Em que posso ser útil?"
            ],
            'how_are_you': [
                "Estou muito bem, obrigada por perguntar! 😊",
                "Estou ótimo! E você? Como está se sentindo?",
                "Tudo bem por aqui! Mas me diga, como você está?"
            ],
            'thanks': [
                "De nada! É um prazer ajudar! 💛",
                "Imagina! Estou sempre aqui para você! 😊",
                "Por nada! Se precisar de mais alguma coisa, é só chamar!"
            ],
            'goodbye': [
                "Tchau! Foi um prazer conversar com você! Até logo! 👋",
                "Adeus! Volte sempre que precisar! 🦊",
                "Tchau! Tomara que eu tenha ajudado! Até a próxima!"
            ],
            'help': [
                "Posso te ajudar de várias formas! Posso responder perguntas, conversar, dar sugestões, ou simplesmente fazer companhia! 😄",
                "Estou aqui para ajudar com o que precisar! Pergunte-me qualquer coisa!",
                "Adoro ajudar! Me diz, o que você gostaria de saber ou fazer?"
            ],
            'joke': [
                "Por que o PROGRAMADOR foi ao terapia? Porque tinha muitos BUGS emocionais! 😄",
                "O que o JavaScript disse para o HTML? Eu te domo do meu jeito! 💻",
                "Por que o computador ficou frio? Porque deixou as janelas abertas! ❄️"
            ],
            'compliment': [
                "Que gentil da sua parte! Você é muito agradável também! 😊",
                "Oh, obrigada! Você é um amor! 💛",
                "Isso me deixa muito feliz! Obrigada pelo carinho!"
            ],
            'default': [
                "Interessante! Me conta mais sobre isso! 🤔",
                "Hmm, não tenho certeza se entendi. Pode me explicar melhor?",
                "Que interessante! O que você gostaria de saber sobre isso?",
                "Entendo! Quer conversar mais sobre isso?",
                "Nossa, isso é muito legal! Me conta mais!"
            ]
        }
    
    def get_response(self, message):
        message_lower = message.lower().strip()
        
        # Detectar saudação
        if any(word in message_lower for word in ['oi', 'ola', 'hello', 'hey', 'bom dia', 'boa tarde', 'boa noite', 'olá', 'oie']):
            return random.choice(self.responses['greeting'])
        
        # Detectar como está
        if any(word in message_lower for word in ['como vai', 'como você está', 'como estas', 'tudo bem', 'como está']):
            return random.choice(self.responses['how_are_you'])
        
        # Detectar agradecimento
        if any(word in message_lower for word in ['obrigado', 'obrigada', 'thanks', 'agradecido', 'grato']):
            return random.choice(self.responses['thanks'])
        
        # Detectar despedida
        if any(word in message_lower for word in ['tchau', 'adeus', 'bye', 'até logo', 'falou', 'vlw']):
            return random.choice(self.responses['goodbye'])
        
        # Detectar pedido de ajuda
        if any(word in message_lower for word in ['ajuda', 'help', 'pode ajudar', 'me ajuda', 'o que faz', 'o que voce faz']):
            return random.choice(self.responses['help'])
        
        # Detectar piada
        if any(word in message_lower for word in ['piada', 'piada de', 'me faz rir', 'conta piada', ' joke']):
            return random.choice(self.responses['joke'])
        
        # Detectar elogio
        if any(word in message_lower for word in ['legal', 'incrivel', 'maravilhoso', 'perfeito', 'bom trabalho', 'bem feito', 'parabens', 'elogio']):
            return random.choice(self.responses['compliment'])
        
        # Se TinyLlama estiver disponível, usar para respostas genéricas
        if USE_LLM and llm_pipeline is not None:
            try:
                # Criar prompt no estilo TinyLlama
                prompt = f"""<system>
Você é o Fox, um assistente virtual amigável, gentil e prestativo. Você sempre responde de forma educada, respeitosa e com empatia. Use emojis ocasionalmente para deixar a conversa mais divertida.
</system>

<user>
{message}
</system>

<assistant>
"""
                result = llm_pipeline(prompt)
                response = result[0]['generated_text']
                # Extrair só a resposta do assistente
                if '<assistant>' in response:
                    response = response.split('<assistant>')[-1].strip()
                # Limpar resposta
                response = response.replace('</assistant>', '').strip()
                # Limitar tamanho
                if len(response) > 500:
                    response = response[:500] + "..."
                return response
            except Exception as e:
                print(f"Erro ao gerar resposta: {e}")
        
        # Resposta padrão (fallback)
        return random.choice(self.responses['default'])

# Instanciar o assistente
assistant = FoxAssistant()

@app.route('/')
def home():
    """Página principal do assistente"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint para processar mensagens do chat"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message.strip():
        return jsonify({'response': 'Olá! Como posso te ajudar hoje?'})
    
    response = assistant.get_response(user_message)
    
    return jsonify({
        'response': response,
        'timestamp': datetime.now().strftime('%H:%M')
    })

@app.route('/greeting', methods=['GET'])
def greeting():
    """Endpoint para obter saudação inicial"""
    return jsonify({
        'greeting': random.choice(assistant.greetings),
        'name': assistant.name
    })

if __name__ == '__main__':
    print("🦊 Fox-AI Starting...")
    print("Acesse: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

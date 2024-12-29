import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# Configure 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,  # Use 4-bit precision
    bnb_4bit_compute_dtype="float16",  # Compute with float16
    bnb_4bit_use_double_quant=True,  # Further reduce memory usage
)

# Load the tokenizer and model with quantization
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-3.1-8B-Instruct",
        quantization_config=bnb_config,
        device_map="auto"  # Automatically distributes model across available GPUs
    )
    return tokenizer, model

tokenizer, model = load_model()

# Streamlit App Title
st.title("📝 Paraphrasing Assistant with LLaMA 🤖")

# Paraphrasing Style Selection
paraphrase_style = st.selectbox(
    "Choose Paraphrasing Style:",
    ["Balanced", "Concise", "Creative"]
)

# Adjust parameters based on style
if paraphrase_style == "Balanced":
    temperature = 0.7
    top_p = 0.9
elif paraphrase_style == "Concise":
    temperature = 0.5
    top_p = 0.85
elif paraphrase_style == "Creative":
    temperature = 0.9
    top_p = 0.95

# User input for text to paraphrase
user_input = st.text_area("Enter your text to paraphrase:", height=200)

# Paraphrasing logic
if st.button("Paraphrase"):
    if user_input:
        with st.spinner("Paraphrasing..."):
            # Enhanced prompt
            prompt = (
                "You are an advanced AI assistant skilled in paraphrasing. "
                "Your task is to rephrase the given text while:\n"
                "- Preserving its original style, tone, and meaning.\n"
                "- Avoiding unnecessary verbosity or over-expansion.\n"
                "- Ensuring the output is natural and flows smoothly.\n\n"
                f"Original Text:\n{user_input}\n\n"
                "Paraphrased Text:"
            )
            
            # Tokenize input and move to device
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=600).to(model.device)
            output = model.generate(
                **inputs,
                max_length=1500,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=1.2,
                pad_token_id=tokenizer.eos_token_id
            )
            paraphrased = tokenizer.decode(output[0], skip_special_tokens=True)
            paraphrased = paraphrased.split("Paraphrased Text:")[-1].strip()
            
            st.success("Paraphrasing Complete!")
            st.write("### Paraphrased Text:")
            st.write(paraphrased)
    else:
        st.warning("Please enter text to paraphrase.")

# Footer
st.markdown("---")
st.markdown("Built using **Streamlit** and **LLaMA-3.1-8B-Instruct** with **4-bit Quantization**.")

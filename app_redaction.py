from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

prompt = "My name is satish, my email is satish.k@test.com, my credit card is 4111 1111 1111 1111, and my insurance number is 123-45-6789."

results = analyzer.analyze(text=prompt, entities=["PERSON", "EMAIL_ADDRESS", "CREDIT_CARD", "US_SOCIAL_SECURITY_NUMBER"], language='en')

anonymized_prompt = anonymizer.anonymize(text=prompt, analyzer_results=results)

print(anonymized_prompt.text)


redaction_map = {}
anonymized_prompt = prompt
for idx, res in enumerate(results):
    placeholder = f"<{res.entity_type}_{idx}>"
    original_value = prompt[res.start:res.end]
    redaction_map[placeholder] = original_value
    anonymized_prompt = anonymized_prompt.replace(original_value, placeholder, 1)

print("Anonymized prompt:", anonymized_prompt)
print("Redaction map:", redaction_map)

def reverse_redact(anonymized_text, redaction_map):
    restored = anonymized_text
    for placeholder, original in redaction_map.items():
        restored = restored.replace(placeholder, original)
    return restored

restored_prompt = reverse_redact(anonymized_prompt, redaction_map)
print("Restored prompt:", restored_prompt)


analyzer = AnalyzerEngine()
supported_entities = analyzer.get_supported_entities(language='en')
print(supported_entities)

#['CREDIT_CARD', 'MEDICAL_LICENSE', 'US_BANK_NUMBER', 'US_SSN', 'US_PASSPORT', 'DATE_TIME', 'URL', 'EMAIL_ADDRESS', 'US_DRIVER_LICENSE', 'PHONE_NUMBER', 'US_ITIN', 'CRYPTO', 'PERSON', 'NRP', 'LOCATION', 'IBAN_CODE', 'IP_ADDRESS', 'UK_NHS']
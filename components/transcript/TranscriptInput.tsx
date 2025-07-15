"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { FileText, Sparkles, Clock, Users } from 'lucide-react'

interface TranscriptInputProps {
  onSubmit: (transcript: string) => void
}

export function TranscriptInput({ onSubmit }: TranscriptInputProps) {
  const [transcript, setTranscript] = useState('')
  const [selectedExample, setSelectedExample] = useState<string | null>(null)

  const examples = [
    {
      id: 'breast-cancer',
      title: 'Breast Cancer Consultation',
      description: 'Oncology consultation for invasive ductal carcinoma',
      category: 'Oncology',
      preview: 'Dr. Martinez: Good morning, Mrs. Chen. I have your test results...',
      transcript: `Dr. Martinez: Good morning, Mrs. Chen. I have your test results. You have been diagnosed with invasive ductal carcinoma of the left breast. You are 58 years old and live in San Francisco.

Mrs. Chen: Oh my... I was afraid of that. Is it... is it bad?

Dr. Martinez: Let me explain what we know. The tumor is approximately 2.5 centimeters in size. The good news is that it appears to be localized, and we haven't found evidence of spread to your lymph nodes.

Mrs. Chen: What does that mean for my treatment?

Dr. Martinez: Your tumor is estrogen receptor positive and HER2 negative. This actually gives us good treatment options. We're staging this as Stage IIA breast cancer. I take lisinopril for my blood pressure and metformin for my diabetes.

Mrs. Chen: Are there any clinical trials I might be eligible for?

Dr. Martinez: That's an excellent question. There are several clinical trials that might be appropriate for someone with your diagnosis. Your profile - a 58-year-old woman with Stage IIA, ER-positive, HER2-negative breast cancer - makes you eligible for several promising studies.`
    },
    {
      id: 'cardiac',
      title: 'Cardiac Consultation',
      description: 'Cardiology consultation for chest pain and coronary disease',
      category: 'Cardiology',
      preview: 'Dr. Thompson: Good afternoon, Mr. Johnson. Tell me about this chest pain...',
      transcript: `Dr. Thompson: Good afternoon, Mr. Johnson. Tell me about this chest pain you've been experiencing.

Mr. Johnson: Good afternoon, Doctor. I'm 67 years old and live in Oakland, CA. The chest pain started about three weeks ago, especially when I walk up stairs or do any physical activity.

Dr. Thompson: Are you experiencing any other symptoms?

Mr. Johnson: Yes, I get short of breath pretty easily now, and sometimes I feel dizzy. I take amlodipine for my blood pressure and atorvastatin for my cholesterol.

Dr. Thompson: Based on your symptoms and test results, you have significant coronary artery disease. You have severe blockages in two of your main coronary arteries.

Mr. Johnson: What are my treatment options?

Dr. Thompson: We have several options including angioplasty and stent placement. However, given your age and the specific pattern of your coronary disease, you might be eligible for some innovative clinical trials looking at new types of stents and minimally invasive procedures.

Mr. Johnson: I'm interested in learning more about those trials.`
    },
    {
      id: 'complex-oncology-long',
      title: 'Complex Cancer Case - Extended Consultation',
      description: 'Long transcript (>2000 words) - Tests Claude LLM routing for complex oncology case',
      category: 'Oncology - Complex',
      preview: 'Dr. Williams: Mrs. Rodriguez, thank you for coming in today. I understand you\'ve been dealing with some concerning symptoms...',
      transcript: `Dr. Williams: Mrs. Rodriguez, thank you for coming in today. I understand you've been dealing with some concerning symptoms over the past few months. Can you tell me about your medical history and what brought you here?

Mrs. Rodriguez: Thank you, Dr. Williams. I'm 52 years old and I live in Austin, Texas. Over the past six months, I've been experiencing increasing fatigue, unexplained weight loss of about 20 pounds, and recently some abdominal pain. My family physician ran some tests and referred me to you because they found some abnormalities in my blood work and imaging.

Dr. Williams: I see. Let's review your complete medical history first. What chronic conditions do you currently have?

Mrs. Rodriguez: I have Type 2 diabetes, which I've had for about 8 years now. I take metformin and glipizide for that. I also have high blood pressure, and I take lisinopril and amlodipine. About three years ago, I was diagnosed with hypothyroidism, so I take levothyroxine for that. I'm also on atorvastatin for high cholesterol.

Dr. Williams: Have you had any previous surgeries or hospitalizations?

Mrs. Rodriguez: Yes, I had a hysterectomy about 10 years ago due to fibroids. I've also had my gallbladder removed about 5 years ago. No other major surgeries. I was hospitalized once for pneumonia about two years ago.

Dr. Williams: Tell me about your family history of cancer or other serious illnesses.

Mrs. Rodriguez: That's actually something that worries me. My mother died of ovarian cancer when she was 58. My maternal aunt also had breast cancer in her early 60s. On my father's side, my grandfather had prostate cancer, and my father has diabetes and heart disease.

Dr. Williams: I understand your concern given that family history. What about your lifestyle factors? Do you smoke or drink alcohol?

Mrs. Rodriguez: I smoked for about 15 years but quit 10 years ago. I occasionally have a glass of wine with dinner, maybe twice a week. I try to stay active, but with the fatigue I've been experiencing, it's been much harder lately.

Dr. Williams: Let's discuss your current symptoms in more detail. You mentioned fatigue, weight loss, and abdominal pain. Can you describe the nature of the abdominal pain?

Mrs. Rodriguez: The pain is mostly in my upper abdomen, sometimes it radiates to my back. It's been getting progressively worse over the past two months. It's not related to eating, and antacids don't help. Sometimes I also feel bloated and have some nausea.

Dr. Williams: Have you noticed any changes in your bowel habits or urination?

Mrs. Rodriguez: Now that you mention it, yes. I've been having some constipation, which is unusual for me. And I've been urinating more frequently, but I thought that might be related to my diabetes.

Dr. Williams: Are you experiencing any shortness of breath, chest pain, or swelling in your legs?

Mrs. Rodriguez: I have been getting short of breath with minimal exertion, which is new for me. No chest pain, but my legs do seem a bit more swollen at the end of the day than usual.

Dr. Williams: Mrs. Rodriguez, I've reviewed your blood work and imaging studies that your family physician ordered. I need to discuss some concerning findings with you. Your CA-125 level is significantly elevated at 180, and your imaging shows a complex mass in your pelvis with some fluid in your abdomen.

Mrs. Rodriguez: What does that mean, doctor? Is it cancer?

Dr. Williams: These findings are concerning and suggest the possibility of ovarian cancer, particularly given your family history and symptoms. However, we need additional tests to confirm the diagnosis and determine the extent of any disease. I'm recommending that we perform a CT scan of your chest, abdomen, and pelvis, and we'll need to do a tissue biopsy.

Mrs. Rodriguez: Oh no... I was afraid of this. What happens if it is cancer?

Dr. Williams: I understand this is frightening news. If it is ovarian cancer, we'll need to determine the stage - that means finding out how far the cancer has spread, if at all. Ovarian cancer is often treatable, especially when caught at earlier stages. The treatment typically involves surgery to remove as much of the cancer as possible, followed by chemotherapy.

Mrs. Rodriguez: What about my other medical conditions? Will they complicate treatment?

Dr. Williams: Your diabetes and blood pressure are important considerations, but they're well-controlled based on your recent lab work. We'll work closely with your endocrinologist and cardiologist to manage these conditions during treatment. Your hypothyroidism is also well-controlled with medication.

Mrs. Rodriguez: Will I be able to continue my current medications?

Dr. Williams: We'll need to review all your medications. The metformin, glipizide, lisinopril, amlodipine, levothyroxine, and atorvastatin can generally be continued, but we may need to adjust doses or timing around chemotherapy treatments. We'll also need to monitor your kidney function closely, especially with some chemotherapy drugs.

Mrs. Rodriguez: Are there any clinical trials that I might be eligible for?

Dr. Williams: That's an excellent question, and I'm glad you're thinking about all your options. Depending on the final diagnosis, staging, and specific characteristics of the cancer, there may indeed be clinical trials available. For ovarian cancer, there are often trials testing new combinations of chemotherapy drugs, immunotherapy approaches, and targeted therapies.

Mrs. Rodriguez: What would make me eligible or ineligible for trials?

Dr. Williams: Several factors determine trial eligibility. Your age of 52 is actually ideal for most trials. Your overall health status, despite the diabetes and other conditions, appears good. The specific type and stage of cancer will be crucial. Some trials are for newly diagnosed patients, while others are for recurrent disease. Your prior treatments, kidney and liver function, and heart function all play a role in eligibility.

Mrs. Rodriguez: What types of trials might be available for someone with my profile?

Dr. Williams: For a 52-year-old woman with newly diagnosed ovarian cancer and well-controlled diabetes and hypertension, there could be several options. There are trials looking at combining traditional chemotherapy with newer immunotherapy drugs like pembrolizumab or bevacizumab. There are also trials studying PARP inhibitors, which are particularly effective in patients with certain genetic mutations like BRCA1 or BRCA2.

Mrs. Rodriguez: Should I get genetic testing?

Dr. Williams: Absolutely. Given your strong family history of ovarian and breast cancer, genetic testing for BRCA1, BRCA2, and other hereditary cancer genes is very important. This information not only helps guide your treatment but also provides important information for your family members.

Mrs. Rodriguez: What about my daughters? Should they be tested too?

Dr. Williams: If we find that you carry a genetic mutation, then yes, your daughters should be counseled about genetic testing when they're appropriate age. The presence of mutations like BRCA1 or BRCA2 significantly increases the risk of breast and ovarian cancers.

Mrs. Rodriguez: How long will all these tests take?

Dr. Williams: We'll expedite everything. The CT scan can be done within the next few days. The biopsy procedure will likely be scheduled within a week, and we'll have results within 3-5 days after that. Genetic testing typically takes 2-3 weeks for results.

Mrs. Rodriguez: And if it is cancer, how quickly do we need to start treatment?

Dr. Williams: Ovarian cancer is generally an aggressive disease, so we don't want to delay treatment unnecessarily. However, we also want to make sure we have all the information we need to choose the best treatment approach, including potential clinical trial participation. Typically, we aim to start treatment within 2-3 weeks of diagnosis.

Mrs. Rodriguez: What about my quality of life during treatment? I'm still working, and I have elderly parents I help care for.

Dr. Williams: That's a very important consideration. Cancer treatment, particularly chemotherapy, does have side effects that can impact quality of life. Common side effects include fatigue, nausea, hair loss, and increased infection risk. However, we have many supportive care measures that can help manage these side effects. We also have social workers who can help you plan for care needs.

Mrs. Rodriguez: Are there any dietary changes I should make, especially with my diabetes?

Dr. Williams: Maintaining good nutrition is crucial during cancer treatment. We'll connect you with an oncology nutritionist who has experience working with diabetic patients. Generally, we recommend a well-balanced diet rich in protein to help your body handle treatment. Your diabetes management may need some adjustments during chemotherapy.

Mrs. Rodriguez: What's the prognosis for ovarian cancer?

Dr. Williams: The prognosis depends heavily on the stage at diagnosis and the specific type of ovarian cancer. When caught early, ovarian cancer has a much better prognosis. Even in more advanced cases, many patients respond well to treatment and go on to have good quality of life for many years. Every case is different, and we'll have a much better idea of your specific situation once we complete the staging workup.

Mrs. Rodriguez: I'm scared, but I want to fight this. What's our next step?

Dr. Williams: I can see you're a strong person, and that will serve you well in this fight. Our immediate next steps are to schedule the CT scan and biopsy. I'm also going to refer you to a genetic counselor for the hereditary cancer testing. Once we have all the results, we'll meet again to discuss the complete treatment plan, including any available clinical trials that might be appropriate for your specific situation.

Mrs. Rodriguez: Thank you, Dr. Williams. I know this is a lot to process, but I appreciate you being so thorough and honest with me.

Dr. Williams: Of course, Mrs. Rodriguez. This is a team effort, and we're going to be with you every step of the way. My nurse will give you some educational materials about ovarian cancer and help you schedule all your appointments. Please don't hesitate to call if you have any questions before our next visit.`
    },
    {
      id: 'rare-disease-complex',
      title: 'Rare Neurological Disease - High Medical Complexity',
      description: 'Complex case with rare diagnosis - Tests high complexity routing to Claude',
      category: 'Neurology',
      preview: 'Dr. Chen: Ms. Kim, I\'ve been reviewing your case with the neurology team...',
      transcript: `Dr. Chen: Ms. Kim, I've been reviewing your case with the neurology team and we have some important findings to discuss. Your presentation with the movement disorder and neurological symptoms has led us to consider some rare conditions.

Ms. Kim: Thank you for seeing me, Dr. Chen. I'm 29 years old and live in Seattle, Washington. These symptoms have been getting progressively worse over the past year and no one has been able to figure out what's wrong.

Dr. Chen: I understand your frustration. Based on your symptoms, genetic testing results, and neuroimaging, we believe you have Huntington's disease, which is a rare autoimmune neurological condition. This is an inherited disorder that affects movement, cognition, and emotional control.

Ms. Kim: Huntington's disease? I've heard of that. Is it... is it fatal?

Dr. Chen: Huntington's disease is a progressive neurodegenerative condition. While it is serious, there are treatments available and research is advancing rapidly. The fact that you're young and we're catching this relatively early in the disease progression gives us more options.

Ms. Kim: What kind of treatments are available?

Dr. Chen: We have several approaches. For the movement symptoms, we can use medications like tetrabenazine or deutetrabenazine. For mood and psychiatric symptoms, we might use antidepressants, antipsychotics, or mood stabilizers. Physical therapy, occupational therapy, and speech therapy are also very important.

Ms. Kim: Are there any clinical trials for Huntington's disease?

Dr. Chen: Yes, and this is actually very exciting. There are several clinical trials currently enrolling patients with Huntington's disease. Some are testing gene therapy approaches, others are looking at neuroprotective medications, and there are trials studying antisense oligonucleotides that could potentially slow disease progression.

Ms. Kim: What would make me eligible for these trials?

Dr. Chen: Your age of 29 is actually ideal for many trials. Most studies are looking for patients in the early stages of the disease, which appears to be your situation. You'll need to have confirmed genetic testing showing the expanded CAG repeat, which you have. Your overall health status is good, and you don't have significant medical comorbidities.

Ms. Kim: What kind of gene therapy are they testing?

Dr. Chen: There are trials looking at using viral vectors to deliver therapeutic genes directly to the brain. There are also studies of antisense oligonucleotides that are designed to reduce the production of the mutant huntingtin protein. These are administered by injection into the spinal fluid.

Ms. Kim: That sounds scary. Are these treatments safe?

Dr. Chen: All clinical trials have rigorous safety monitoring. The gene therapy and antisense approaches have shown promising results in animal studies and early-phase human trials. The injection procedures are performed by experienced teams, and you would be monitored very closely throughout the study.

Ms. Kim: How do I find out about these trials?

Dr. Chen: I work closely with several research centers that conduct Huntington's disease trials. There's a major study happening at the University of Washington, which is convenient for you in Seattle. There are also trials at Stanford, UCSF, and Johns Hopkins that might be options.

Ms. Kim: What's the time commitment for participating in a trial?

Dr. Chen: It varies by study, but typically you'd need to visit the research center every 1-3 months for evaluations. Some studies require overnight stays for certain procedures. The total study duration is usually 1-2 years, with possible extension phases if the treatment shows benefit.

Ms. Kim: Will my insurance cover the trial costs?

Dr. Chen: The research sponsor covers all study-related costs, including the experimental treatment, study visits, and required tests. Your regular insurance would still cover your routine medical care. Many trials also provide travel reimbursement.

Ms. Kim: What if the experimental treatment doesn't work or makes me worse?

Dr. Chen: That's a valid concern. All trials have stopping rules - if there are safety concerns or if the treatment isn't working, you can discontinue at any time. You'll continue to receive the standard of care regardless of trial participation. The research teams are very experienced in managing these conditions.

Ms. Kim: Are there any lifestyle changes I should make?

Dr. Chen: Yes, staying physically active is very important. Regular exercise has been shown to help with both motor symptoms and mood in Huntington's disease. A healthy diet, adequate sleep, and stress management are also crucial. We'll connect you with a specialized physical therapist.

Ms. Kim: What about planning for the future? Should I be thinking about advance directives?

Dr. Chen: It's wise to think about these things while you're able to make clear decisions. Huntington's disease can eventually affect cognitive function, so having advance directives and healthcare proxies in place is important. Our social worker can help you with this planning.

Ms. Kim: Should my family members be tested for the gene?

Dr. Chen: That's a very personal decision. Since Huntington's disease is inherited, your siblings and potentially your children could be at risk. We strongly recommend genetic counseling to discuss the implications of testing for family members. Not everyone chooses to be tested, and that's completely understandable.

Ms. Kim: I'm interested in learning more about the clinical trials. What's the next step?

Dr. Chen: I'm going to connect you with Dr. Sarah Martinez, who is the principal investigator for the Huntington's disease trials at the University of Washington. She can provide detailed information about current studies and determine if you might be eligible. I'll also give you information about the Huntington's Disease Society of America, which has excellent resources and support groups.`
    },
    {
      id: 'diabetes-eligibility-test',
      title: 'Type 1 Diabetes - Eligibility Testing',
      description: 'Tests specific eligibility criteria and age-based matching',
      category: 'Endocrinology',
      preview: 'Dr. Patel: Hello Sarah, I see you\'re here for your diabetes management follow-up...',
      transcript: `Dr. Patel: Hello Sarah, I see you're here for your diabetes management follow-up. How are you feeling today?

Sarah: Hi Dr. Patel. I'm doing okay, but I'm still struggling with my blood sugar control. I'm 24 years old and live in Boston, Massachusetts. I was diagnosed with Type 1 diabetes when I was 12.

Dr. Patel: Let's review your current management. What insulin regimen are you on?

Sarah: I'm using an insulin pump with Humalog. I also take levothyroxine for hypothyroidism that developed a few years after my diabetes diagnosis. Sometimes I take ibuprofen for headaches.

Dr. Patel: I see your HbA1c is 8.2%, which is higher than we'd like to see. Have you been experiencing frequent highs and lows?

Sarah: Yes, that's been really frustrating. I'll have days where my sugar is 300, then a few hours later I'm having a low blood sugar episode. It's been affecting my work and social life.

Dr. Patel: I understand that must be very challenging. Have you considered continuous glucose monitoring?

Sarah: I tried it briefly but had some insurance issues. I'm interested in trying again, especially if there are newer options available.

Dr. Patel: There actually are some exciting developments in diabetes technology. I wanted to discuss with you some clinical trials that are testing new diabetes management systems and treatments.

Sarah: Really? I'd be very interested in that. What kind of trials?

Dr. Patel: There are several types. Some are testing closed-loop insulin pump systems - these are sometimes called artificial pancreas systems. Others are testing new types of insulin that work faster or last longer. There are also trials looking at immunotherapy to preserve remaining beta cell function.

Sarah: Would I be eligible for any of these?

Dr. Patel: Your age of 24 makes you eligible for most diabetes trials. The fact that you have Type 1 diabetes diagnosed in childhood, you're on insulin pump therapy, and you have some challenges with glucose control actually makes you a good candidate for several studies.

Sarah: What about my thyroid condition? Would that disqualify me?

Dr. Patel: Hypothyroidism is actually quite common in people with Type 1 diabetes, and most trials allow patients with well-controlled thyroid disease. Since you're on stable levothyroxine replacement, that shouldn't be a barrier.

Sarah: Are there any trials specifically for young adults with diabetes?

Dr. Patel: Yes, there are several trials that focus on the 18-30 age group. Young adults with Type 1 diabetes often have unique challenges with diabetes management related to lifestyle, work, and social factors. There's one study at Joslin Diabetes Center that's specifically designed for people your age.

Sarah: What would participating in a trial involve?

Dr. Patel: It depends on the specific study, but typically you'd have more frequent clinic visits - maybe once a month instead of every three months. You'd get more detailed glucose monitoring, and if it's a technology study, you might get to use newer devices before they're commercially available.

Sarah: That actually sounds appealing. I feel like I need more support with my diabetes management.

Dr. Patel: Many trial participants find that the extra attention and monitoring helps improve their diabetes control even beyond the study period. You'd also be contributing to research that could help other young people with diabetes.

Sarah: Are there any risks I should know about?

Dr. Patel: All trials have potential risks, but diabetes technology trials are generally quite safe. The main risks might be related to device malfunctions or temporary changes in your diabetes routine while adjusting to new treatments. All studies have safety monitoring and you can withdraw at any time.

Sarah: What's the time commitment typically like?

Dr. Patel: Most diabetes trials run for 3-6 months, with some having optional extension phases. You'd typically need to come in for study visits once a month, and there might be some additional remote monitoring or phone check-ins.

Sarah: I'm interested. How do I get more information?

Dr. Patel: I can refer you to the research coordinators at several centers. There's ongoing research at Joslin, Mass General, and Harvard's diabetes research group. I'll give you contact information and they can screen you for current studies that might be a good fit.

Sarah: Will this interfere with my regular diabetes care?

Dr. Patel: Not at all. The research teams work closely with your regular endocrinologist - that's me - to coordinate care. Often, trial participation actually enhances your regular diabetes management.

Sarah: This sounds like it could really help me. What's the next step?

Dr. Patel: I'll send your information to the research coordinators at Joslin and Mass General. They'll call you within the next week to discuss current trials and see which ones might be appropriate for someone with your diabetes history and goals.`
    },
    {
      id: 'geographic-diversity-rural',
      title: 'Rural Patient - Geographic Matching Test',
      description: 'Tests geographic matching and travel willingness for rural patients',
      category: 'Family Medicine',
      preview: 'Dr. Rodriguez: Good morning, Mr. Anderson. I appreciate you making the drive from Wyoming...',
      transcript: `Dr. Rodriguez: Good morning, Mr. Anderson. I appreciate you making the drive from Wyoming to see our specialists here in Denver.

Mr. Anderson: Good morning, Dr. Rodriguez. Thank you for seeing me. I'm 45 years old and I live in a small town called Gillette in northeastern Wyoming. There aren't many specialists where I live, so I'm used to traveling for medical care.

Dr. Rodriguez: I understand. Rural healthcare can be challenging. Tell me about what's been concerning you.

Mr. Anderson: I've been having some digestive issues for the past six months. Stomach pain, changes in my bowel habits, and I've lost about 15 pounds without trying. My family doctor in Gillette ran some tests and thinks I might need to see a gastroenterologist or oncologist.

Dr. Rodriguez: What's your medical history like?

Mr. Anderson: I'm pretty healthy overall. I have high blood pressure, and I take amlodipine for that. I work on a ranch, so I'm physically active. I don't smoke anymore - quit about 5 years ago after smoking for 20 years. I have maybe two beers a week.

Dr. Rodriguez: Any family history of cancer or digestive diseases?

Mr. Anderson: My father had colon cancer when he was in his 60s. My mother is still alive and healthy at 78. I have two brothers, both healthy as far as I know.

Dr. Rodriguez: Based on your symptoms and family history, we need to do some additional testing. This could include a colonoscopy and possibly some imaging studies.

Mr. Anderson: I expected that. How often would I need to come to Denver for appointments?

Dr. Rodriguez: That depends on what we find. If we do discover something that needs treatment, the frequency would vary. Some treatments might require weekly visits initially, others might be monthly.

Mr. Anderson: I'm willing to travel for good medical care. It's about a 4-hour drive each way, but I've done it before. My wife usually comes with me, and we sometimes make it a little trip to the city.

Dr. Rodriguez: That's good to hear. Many of our rural patients find that combining medical appointments with other activities in Denver helps make the travel worthwhile. Are you open to participating in clinical trials if appropriate?

Mr. Anderson: I'd consider it. What kind of trials might be relevant?

Dr. Rodriguez: Depending on what we find, there could be trials for digestive disorders or, if needed, cancer treatment trials. Many trials are specifically designed to accommodate patients who live far from the research center.

Mr. Anderson: How would that work practically?

Dr. Rodriguez: Many trials have accommodations for rural patients. Some provide travel reimbursement or lodging assistance. Others have modified visit schedules that group multiple appointments into fewer trips. There are also some trials that allow certain visits to be done at local healthcare facilities closer to your home.

Mr. Anderson: That would be helpful. The travel costs can add up, especially if I need frequent visits.

Dr. Rodriguez: Absolutely. Research sponsors understand that geographic barriers can prevent participation, so many studies have support systems in place. Some even coordinate with local healthcare providers in Wyoming to share certain aspects of care.

Mr. Anderson: Are there any trials that focus on patients from rural areas?

Dr. Rodriguez: There are some studies specifically designed to address healthcare disparities in rural populations. These often have enhanced support services and may study whether telemedicine or remote monitoring can be effective for certain treatments.

Mr. Anderson: I'm definitely interested in learning more. My local doctor back home is pretty good - Dr. Susan Miller in Gillette. Would she be involved?

Dr. Rodriguez: Many clinical trials encourage coordination with local physicians. Dr. Miller could potentially provide routine monitoring or follow-up care, which would reduce your travel burden. The research team would work with her to ensure continuity of care.

Mr. Anderson: What about emergency situations? If I'm in a trial and something happens, what do I do from Wyoming?

Dr. Rodriguez: All clinical trials have 24/7 contact numbers for emergencies. They also provide detailed instructions to local emergency rooms about study-related concerns. Your local hospital in Gillette would be informed about your participation and any special considerations.

Mr. Anderson: How do I find out about trials that might be appropriate for someone in my situation?

Dr. Rodriguez: Once we complete your diagnostic workup, I'll connect you with our research coordinators. They maintain relationships with research centers throughout the Rocky Mountain region and can identify studies that accommodate rural patients.

Mr. Anderson: Are there research centers closer to Wyoming that I should know about?

Dr. Rodriguez: The University of Utah in Salt Lake City is actually closer to you than Denver and has several active research programs. There's also some research activity in Billings, Montana. Depending on what we find, those might be options to consider.

Mr. Anderson: I appreciate you thinking about the practical aspects of this. It makes me more confident about pursuing treatment options, including research studies.

Dr. Rodriguez: Of course. Rural patients face unique challenges, and it's important that research opportunities are accessible. Let's get your diagnostic tests scheduled, and then we'll have a much better idea of what options might be available for you, including any relevant clinical trials.`
    },
    {
      id: 'pediatric-transition',
      title: 'Pediatric to Adult Transition - Age Testing',
      description: 'Tests age boundaries and transition between pediatric and adult trials',
      category: 'Pediatric Hematology',
      preview: 'Dr. Kim: Hello Maya, and hello Mrs. Patel. Maya, you\'re turning 18 next month...',
      transcript: `Dr. Kim: Hello Maya, and hello Mrs. Patel. Maya, you're turning 18 next month, which is an important milestone in your leukemia treatment journey.

Maya: Hi Dr. Kim. Yeah, it's kind of scary thinking about transitioning to adult care, but also exciting.

Mrs. Patel: Dr. Kim, we're concerned about what this transition means for Maya's treatment options. She lives with us in Portland, Oregon, and we want to make sure she continues to get the best care possible.

Dr. Kim: I understand your concerns completely. Maya, you've been doing well on your current treatment for acute lymphoblastic leukemia. Your recent bone marrow biopsy shows continued remission.

Maya: That's good news. But what does turning 18 mean for my treatment? Will everything change?

Dr. Kim: The good news is that your current treatment protocol doesn't need to change just because you're turning 18. However, you will be transitioning from pediatric to adult hematology care, and this opens up some new opportunities, including different clinical trials.

Maya: What kind of trials might be available for someone my age?

Dr. Kim: This is actually an interesting time in your treatment journey. At 18, you might be eligible for both young adult trials and some adult trials. There are specific studies designed for adolescents and young adults with ALL - the AYA population, as we call it.

Mrs. Patel: What makes the young adult trials different from pediatric trials?

Dr. Kim: Young adult ALL trials often use treatment approaches that bridge pediatric and adult protocols. They recognize that biology and treatment response in teenagers and young adults can be different from both younger children and older adults.

Maya: Would I still be eligible for any pediatric trials since I'm not quite 18 yet?

Dr. Kim: That's a great question. Some pediatric trials allow patients up to age 21 or even 25, especially for cancers that typically occur in young people. Others have strict age cutoffs at 18. Each study has specific eligibility criteria.

Maya: What about after I turn 18? What options would be available then?

Dr. Kim: There are several ongoing trials specifically for young adults with ALL. Some are testing new combinations of chemotherapy, others are looking at immunotherapy approaches like CAR-T cell therapy, and there are trials studying targeted therapies based on specific genetic markers.

Maya: CAR-T cell therapy sounds interesting. What is that?

Dr. Kim: CAR-T cell therapy involves taking your own immune cells, modifying them in a laboratory to better fight your leukemia, and then giving them back to you. It's shown very promising results in young adults with ALL, especially for relapsed or refractory disease.

Mrs. Patel: Is Maya a candidate for these newer therapies?

Dr. Kim: Maya's in remission, so these therapies might be more relevant if her leukemia were to relapse. However, there are also trials studying these approaches in earlier phases of treatment or as consolidation therapy to prevent relapse.

Maya: How do I make decisions about trials when I turn 18? Will my parents still be involved?

Dr. Kim: When you turn 18, you'll be making your own medical decisions. However, most young adults still want their parents involved in these important decisions, and that's completely normal and appropriate. The research teams are experienced in working with young adults and their families.

Maya: Are there support services specifically for young adults in cancer trials?

Dr. Kim: Yes, many cancer centers have specialized programs for adolescents and young adults. These include social workers who understand the unique challenges of being a young adult with cancer, support groups with peers your age, and resources for educational and career planning.

Mrs. Patel: What about college? Maya was planning to start college in the fall.

Dr. Kim: That's definitely something we can work around. Many young adult cancer patients continue their education during treatment. Some trials have flexible scheduling that accommodates school schedules, and many colleges have good support services for students with medical conditions.

Maya: Would participating in a trial interfere with going to college?

Dr. Kim: It depends on the specific trial, but many can be accommodated. Some trials require weekly visits initially, while others might be monthly. We can look for studies that fit with your educational goals. There are also some studies that include telemedicine components.

Maya: What if I want to go to college out of state?

Dr. Kim: That's more challenging but not impossible. Some multi-center trials have sites in different states, so you might be able to transfer your care to a center near your college. This is something we'd need to plan carefully.

Maya: Are there any trials that focus specifically on the transition from pediatric to adult care?

Dr. Kim: That's a very insightful question. There are some studies looking at the best ways to manage this transition and whether different approaches to supportive care improve outcomes in young adults.

Maya: I'm interested in learning more about my options. What's the next step?

Dr. Kim: I'm going to connect you with our adolescent and young adult cancer program coordinator. She can provide information about current trials that might be appropriate for someone your age and situation. We'll also start the process of introducing you to the adult hematology team so the transition is smooth.

Mrs. Patel: Will Maya continue to see you, or will she have a completely new doctor?

Dr. Kim: The transition is gradual. Maya will start meeting with the adult hematology team while still seeing me, so she can get comfortable with the new team. The goal is to ensure continuity of care while opening up new treatment opportunities that come with being an adult patient.`
    }
  ]

  const handleExampleSelect = (example: any) => {
    setSelectedExample(example.id)
    setTranscript(example.transcript)
  }

  const handleSubmit = () => {
    if (transcript.trim()) {
      onSubmit(transcript)
    }
  }

  const wordCount = transcript.trim().split(/\s+/).filter(word => word.length > 0).length

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300">
            <FileText className="h-6 w-6" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Input Patient Transcript
        </h2>
        <p className="mt-2 text-gray-600 dark:text-gray-300">
          Paste your patient-doctor conversation transcript to find matching clinical trials
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Example Transcripts */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Sparkles className="h-5 w-5 text-yellow-500" />
            <Label className="text-lg font-semibold">Example Transcripts</Label>
          </div>
          
          <div className="space-y-3">
            {examples.map((example) => (
              <Card 
                key={example.id}
                className={`cursor-pointer transition-all hover:shadow-md ${
                  selectedExample === example.id 
                    ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                    : ''
                }`}
                onClick={() => handleExampleSelect(example)}
              >
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {example.title}
                        </h3>
                        <Badge variant="outline" className="text-xs">
                          {example.category}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                        {example.description}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                        "{example.preview}"
                      </p>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Transcript Input */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="transcript" className="text-lg font-semibold">
              Patient Transcript
            </Label>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <div className="flex items-center space-x-1">
                <Clock className="h-4 w-4" />
                <span>~2 min</span>
              </div>
              <div className="flex items-center space-x-1">
                <Users className="h-4 w-4" />
                <span>{wordCount} words</span>
              </div>
            </div>
          </div>
          
          <Textarea
            id="transcript"
            placeholder="Paste your patient-doctor conversation transcript here..."
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            className="min-h-[400px] text-sm leading-relaxed resize-none"
          />
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <div className="flex items-center space-x-1">
                <div className={`h-2 w-2 rounded-full ${
                  wordCount > 50 ? 'bg-green-500' : 'bg-yellow-500'
                }`} />
                <span>
                  {wordCount > 50 ? 'Ready to process' : 'Need more content'}
                </span>
              </div>
            </div>
            
            <Button
              onClick={handleSubmit}
              disabled={!transcript.trim() || wordCount < 10}
              className="px-8"
            >
              <Sparkles className="mr-2 h-4 w-4" />
              Analyze Transcript
            </Button>
          </div>
        </div>
      </div>

      <Separator />

      {/* Privacy Notice */}
      <Card className="bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800">
        <div className="p-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-blue-600 dark:bg-blue-800 dark:text-blue-200">
                <Users className="h-4 w-4" />
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-blue-900 dark:text-blue-100">
                Privacy & Security
              </h3>
              <p className="text-sm text-blue-800 dark:text-blue-200 mt-1">
                Patient data is processed securely and not stored permanently. 
                PHI is automatically sanitized before processing.
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}
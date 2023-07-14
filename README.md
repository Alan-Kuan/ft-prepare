# ft-prepare
A simple demo of converting Q&A pairs from Azure Cognitive Services into a format ready for fine-tuning OpenAI GPT models

## Guides
1. Fill in credentials of your Cognitive Service.  
    ![credentials.png](https://github.com/Alan-Kuan/ft-prepare/assets/24734750/c3684730-18c6-4fbe-87fa-4ace0145b37d)
2. Fill in the source URL of the Q&A and then click "Parse".  
    ![parse.png](https://github.com/Alan-Kuan/ft-prepare/assets/24734750/8c847fc0-8c20-40a5-941e-05f1b790204f)
3. You can click "Status" at any time to check the progress.
    It will show "succeeded" when finished.  
    ![status.png](https://github.com/Alan-Kuan/ft-prepare/assets/24734750/471251c0-4eb3-4b06-854a-ff777d4948df)
4. After it finished, click "Fetch" to get processed Q&A pairs.  
    ![fetch.png](https://github.com/Alan-Kuan/ft-prepare/assets/24734750/c4e0c8c5-06d2-4c44-bbab-41315aff2a4f)
5. Then, we can click "Convert" to get transformed data, which is ready for fine tuning.
     ![convert.png](https://github.com/Alan-Kuan/ft-prepare/assets/24734750/49595a19-d90b-4d49-874e-3d10218cd7a7)
6. Finally, click "Download" to save it.

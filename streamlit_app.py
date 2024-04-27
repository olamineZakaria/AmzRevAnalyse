import streamlit as st
import requests
import Amazon as am
import plotly.express as px
st.title("Review Reveal")
with st.sidebar:
    image_url = 'our Logo'
    st.markdown(
    f"""
    <style>
        .image-container {{
            text-align: center;
            padding-top: 0;  # Supprimer le padding en haut
        }}
    </style>
    <div class= "image-container">
        <img src="{image_url}"style="width:100px;">
        <h1><u>Review Reveal</u></h1>
    </div>
    """,
    unsafe_allow_html=True
    )
    st.header("a propose de projet")
    description = """
    Cette application utilise Streamlit pour analyser les avis des produits sur Amazon.
    Elle fournit des analyses de sentiments et des informations sur les produits, 
    permettant aux utilisateurs de prendre des décisions d'achat éclairées.
    """
    st.markdown(description)
    github_link = """
    [Consultez le code source sur GitHub](https://github.com/)
    """
    st.markdown(github_link)
    linkedin_icon_url = "https://cdn-icons-png.flaticon.com/256/174/174857.png"
    st.header("equipe")
    equipe = """
    - [El ouankrimi ali](https://www.linkedin.com/in/alielouankrimi/)
    - [Olamine zakaria](https://www.linkedin.com/in/zakaria-olamine-20031115oz)
    - [Oubella abdallah](https://www.linkedin.com/in/abdallah-oubella-2b5662239/)
    """
    st.markdown(equipe)
url_produit = st.text_input("Entrez l'URL du produit Amazon:", placeholder="https://www.amazon.com/SAMSUNG-Android-Speakers-Upgraded-Graphite/dp/B0CLF2DNMV")
if st.button("Analyser"):
    with st.spinner("Analyse en cours ..."):
        try:
            reponse = requests.get(url_produit)
            if reponse.status_code==200:
                st.success("La verification de URL est avec success Analyse en cours, soyez patient...")
                st.header("Informations générales sur le produit")
                product_name = am.get_product_name(url_produit)
                global_rating = am.get_global_rating(url_produit)
                stars = am.get_rating(url_produit)
                col1, col2 = st.columns([1, 1])
                image_url = am.get_image_url(url_produit)
                col1.image(image_url, caption='Image du produit', width=250)
                col2.text(product_name)
                col2.text(am.get_global_rating(url_produit))
                col2.text(stars)
                df = am.comment_dataFrame(url_produit)
                print(df.shape[0])
                xx = am.sentiemnt_by_comment(df)
                x = px.bar(xx,x='sentiment',y='comment')
                st.plotly_chart(x)
                positive_comments = df[df['sentiment'] == 'Positive']['comment']
                positive_text = ' '.join(positive_comments)
                wordcloud = am.WordCloud(width=800, height=400, background_color='white').generate(positive_text)
                fig = px.imshow(wordcloud.to_array(), binary_string=True)
                fig.update_layout(title='Word Cloud for Positive Comments')
                st.plotly_chart(fig)
                negative_comments = df[df['sentiment'] == 'Negative']['comment']
                negative_text = ' '.join(negative_comments)
                wordcloud = am.WordCloud(width=800, height=400, background_color='white').generate(negative_text)
                fig = px.imshow(wordcloud.to_array(), binary_string=True)
                fig.update_layout(title='Word Cloud for Negative Comments')
                st.plotly_chart(fig)
                neutral_comments = df[df['sentiment']=='Neutral']['comment']
                neutral_text = ' '.join(neutral_comments)
                wordcloud = am.WordCloud(width=800,height=400,background_color='white').generate(neutral_text)
                fig = px.imshow(wordcloud.to_array(),binary_string=True)
                fig.update_layout(title='Word Cloud for Neutral Comments')
                st.plotly_chart(fig)
                #####By chatGpt##########################################
                # st.header("Analyse thématique avec LDA")
                # st.write("Analyse des thèmes principaux des avis")
                # vectorizer = am.CountVectorizer() 
                # X = vectorizer.fit_transform(df['comment'])
                # lda = am.LatentDirichletAllocation(n_components=5, random_state=42)
                # lda.fit(X)
                # feature_names = vectorizer.get_feature_names_out()
                # for topic_idx, topic in enumerate(lda.components_):                              
                #     st.subheader(f"Sujet {topic_idx}:")                                          
                #     st.write(" ".join([feature_names[i] for i in topic.argsort()[:-10 - 1:-1]]) 
                ####################################################################################
            else:
                st.error("La verification de Url est echouee Merci de verifier URL de votre produit")
        except Exception as e:
            st.error(f"Erreur pendant l'analyse : {str(e)}")

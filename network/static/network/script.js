document.addEventListener('DOMContentLoaded', function() {
    addComments();
    addLikeButtons();
});


function addComments() {
    // Haetaan kaikki .post-all-comments
    const comment_sections = document.querySelectorAll('.post-all-comments');
    // Loopataan niiden läpi
    comment_sections.forEach(function(section) {
        const post_id = section.dataset.postId;

        // Haetaan kommentit
        fetch(`/comments/${post_id}`)
        .then(response => response.json())
        .then(comments => {
            comments.forEach(function(comment) {
                const post_div = document.createElement("div");
                post_div.className = "comment-container"

                // Kuvan div
                const photo_div = document.createElement("div");
                photo_div.className = "comment-photo";
                photo_div.innerHTML = `<img src="${comment.user_photo}" alt="image">`

                // Nimimerkin div
                const username_div = document.createElement("div");
                username_div.className = "comment-username";
                username_div.innerHTML = comment.user_username;

                // Kommentin sisällön div
                const content_div = document.createElement("div");
                content_div.className = "comment-content";
                content_div.innerHTML = comment.comment_content;

                // Lisätään kommentti .post-all-comments
                const comment_text_div = document.createElement("div");
                comment_text_div.className = "comment-text-container";
                comment_text_div.append(username_div, content_div);
                post_div.append(photo_div, comment_text_div);
                section.append(post_div);
            })
        })
    });
};


function addLikeButtons() {

    // Tähän blokki, joka ensin poistaa namiskat, jos sellaisia on
    const buttons = document.querySelectorAll(".like-button");
    buttons.forEach(function(button) {
        button.remove();
    });

    // Lopuksi lisätään namiskat
    const postBottomDivs = document.querySelectorAll(".post-bottom");
    postBottomDivs.forEach(function(bottomDiv) {
        const post_id = bottomDiv.dataset.postId;
        fetch(`/post/${post_id}`)
        .then(response => response.json())
        .then(post => {
            if (post["current_user_likes"] === false) {
                // laitetaan like-nappi
                const likeButtonDiv = document.createElement("div");
                likeButtonDiv.className = "like-button";
                likeButtonDiv.id = "like";
                likeButtonDiv.dataset.postId = bottomDiv.dataset.postId;
                likeButtonDiv.innerHTML = '<button type="button">Like</button>';
                bottomDiv.append(likeButtonDiv);
                // event listener
                likeButtonDiv.addEventListener("click", likeUnlike);
            } else {
                // laitetaan unlike-nappi
                const likeButtonDiv = document.createElement("div");
                likeButtonDiv.className = "like-button";
                likeButtonDiv.id = "unlike";
                likeButtonDiv.dataset.postId = bottomDiv.dataset.postId;
                likeButtonDiv.innerHTML = '<button type="button">Unlike</button>';
                bottomDiv.append(likeButtonDiv);
                // event listener
                likeButtonDiv.addEventListener("click", likeUnlike);
            }
        })
    })
};


function likeUnlike() {
    const post_id = this.dataset.postId;
    if (this.id === "like") {
        fetch(`/post/${post_id}`, {
            method: "PUT",
            body: JSON.stringify({
                like: true
            })
        })
        .then(response => {
            addLikeButtons();
        })
    } else {
        fetch(`/post/${post_id}`, {
            method: "PUT",
            body: JSON.stringify({
                like: false
            })
        })
        .then(response => {
            addLikeButtons();
        })
    }
}


document.addEventListener('DOMContentLoaded', function() {
    addComments();
    addLikeButtons();
    addFollowButtons();
    addEditButtons();
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
    const texts = document.querySelectorAll(".like-info");
    texts.forEach(function(text) {
        text.remove();
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

                // Like napin viereen teksti, jos on
                if (post["like_text"] != null) {
                    const infoDiv = document.createElement("div");
                    infoDiv.className = "like-info";
                    infoDiv.append(post["like_text"]);
                    bottomDiv.append(infoDiv);
                }

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
                
                // Like napin viereen teksti, jos on
                if (post["like_text"] != null) {
                    const infoDiv = document.createElement("div");
                    infoDiv.className = "like-info";
                    infoDiv.append(post["like_text"]);
                    bottomDiv.append(infoDiv);
                }

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


function addFollowButtons() {

    // Tähän blokki, joka ensin poistaa namiskat, jos sellaisia on
    const buttons = document.querySelectorAll(".post-username-follow");
    buttons.forEach(function(button) {
        button.remove();
    });

    // Lopuksi lisätään namiskat
    const post_top_divs = document.querySelectorAll(".post-top");
    post_top_divs.forEach(function(top_div) {
        var post_user_id = top_div.dataset.postUserId;
        // Fetchataan postaajan id :llä ja tarkistetaan, seuraako nykyinen käyttäjä postaajaa
        fetch(`/data/user/${post_user_id}`)
        .then(response => response.json())
        .then(data => {
            if (data["current_user_follows"] === true) {
                const follow_button_div = document.createElement("div");
                follow_button_div.className = "post-username-follow";
                follow_button_div.id = "unfollow";
                follow_button_div.dataset.userId = post_user_id;
                follow_button_div.innerHTML = "<button>Unfollow</button>";
                top_div.querySelector(".post-extra-buttons").append(follow_button_div);
                follow_button_div.addEventListener("click", followUnfollow);

            } else if (data["current_user_follows"] === false) {
                const follow_button_div = document.createElement("div");
                follow_button_div.className = "post-username-follow";
                follow_button_div.id = "follow";
                follow_button_div.dataset.userId = post_user_id;
                follow_button_div.innerHTML = "<button>Follow</button>";
                top_div.querySelector(".post-extra-buttons").append(follow_button_div);
                follow_button_div.addEventListener("click", followUnfollow);
            }
        })
    })
};


function followUnfollow() {
    const user_id = this.dataset.userId;

    if (this.id === "follow") {
        fetch(`/data/user/${user_id}`, {
            method: "PUT",
            body: JSON.stringify({
                current_user_follows: true
            })
        })
        // Laitetaan nappi vasta sitten, kun API on antanut vastauksen
        .then(data => {
            addFollowButtons();
        })

    } else if (this.id === "unfollow") {
        fetch(`/data/user/${user_id}`, {
            method: "PUT",
            body: JSON.stringify({
                current_user_follows: false
            })
        })
        // Laitetaan nappi vasta sitten, kun API on antanut vastauksen
        .then(data => {
            addFollowButtons();
        })
    }
}


function addEditButtons() {

    // Poistetaan vanhat painikkeet, jos on
    const buttons = document.querySelectorAll(".post-edit-button");
    buttons.forEach(function(button) {
        button.remove();
    });

    // Lisätään uudet painikkeet
    const post_top_divs = document.querySelectorAll(".post-top");
    post_top_divs.forEach(function(top_div) {
        var post_user_id = top_div.dataset.postUserId;

        fetch(`/data/user/${post_user_id}`)
        .then(response => response.json())
        .then(data => {
            if (data["current_user_is_user"] === true) {
                const edit_button_div = document.createElement("div");
                edit_button_div.className = "post-edit-button";
                edit_button_div.innerHTML = "<button>Edit</button>";
                top_div.querySelector(".post-extra-buttons").append(edit_button_div);
                edit_button_div.addEventListener("click", editPost);
            }
        })
    })
};


function editPost() {
    console.log("button clicked!");

    // Lisätään textarea
    const post = this.parentElement.parentElement.parentElement;
    var post_content = post.querySelector(".post-content")
    var textarea = document.createElement("div");
    textarea.innerHTML = `<textarea>${post_content.innerText.trim()}</textarea>`;
    post_content.innerHTML = textarea.innerHTML;

    // Lisätään uudet painikkeet
    var edit_button = post.querySelector(".post-edit-button");
    edit_button.remove();

    var save_button = document.createElement("div");
    save_button.className = "post-save-button";
    save_button.innerHTML = "<button>Save</button>";

    var delete_button = document.createElement("div");
    delete_button.className = "post-delete-button";
    delete_button.innerHTML = "<button>Delete</button>";

    extra_buttons = post.querySelector(".post-extra-buttons");
    extra_buttons.append(save_button);
    extra_buttons.append(delete_button);

    // Lisätään event listenerit
    save_button.addEventListener("click", saveEdit);
    delete_button.addEventListener("click", deletePost);
}


//Event handler Save-napille
function saveEdit() {

    var post = this.parentElement.parentElement.parentElement;
    const post_id = post.querySelector(".post-bottom").dataset.postId
    var post_content = post.querySelector("textarea").value;
    console.log(post_content);

    fetch(`post/${post_id}`, {
        method: "PUT",
        body: JSON.stringify({
            edited_post: post_content
        })
    })
    // Mitä tapahtuu, kun serveri vastaa
    .then(data => {
        console.log(data);

        // Poistetaan vanhat painikkeet
        var buttons = document.querySelectorAll(".post-save-button");
        buttons.forEach(function(button) {
            button.remove();
        })
        var buttons = document.querySelectorAll(".post-delete-button");
        buttons.forEach(function(button) {
            button.remove();
        })

        // Lisätään uudet edit-painikkeet
        addEditButtons()

        // Korvataan textarea päivitetyllä sisällöllä
        post.querySelector(".post-content").innerHTML = post_content;
    })
};


//Event handler Delete-napille
function deletePost() {

    var post = this.parentElement.parentElement.parentElement;
    const post_id = post.querySelector(".post-bottom").dataset.postId

    fetch(`post/${post_id}`, {
        method: "PUT",
        body: JSON.stringify({
            delete: true
        })
    })
    .then(data => {
        post.parentElement.style.animationPlayState = "running";
        post.parentElement.addEventListener("animationend", () => {
            post.parentElement.remove();
        })
    })
};


console.log("Getting links...");

fetch("https://localhost:5000/get_links")
  .then((response) => response.json())
  .then((data) => {
    const header_div = document.getElementById("headers");
    Object.entries(data).forEach(([key, value]) => {
      const headers = value.header;
      headers.forEach((link) => {
        const p_elm = document.createElement("a");
        const horizontal_line = document.createElement("hr");
        link = link.replace("<", "").replace(">", "");

        if (link.indexOf("https") != -1)
          link = link.replace("<https://", "").replace(">", ""); 
        else if (link.indexOf("mailto:")) 
          link = link.replace("<mailto:", "").replace(">", "");

        p_elm.href = link
        p_elm.innerText = link

        header_div.append(p_elm);
        header_div.append(horizontal_line)
      });
    });
  });


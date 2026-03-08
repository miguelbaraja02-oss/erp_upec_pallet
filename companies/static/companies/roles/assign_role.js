document.addEventListener("DOMContentLoaded",function(){

document.querySelectorAll("select").forEach(select=>{

const wrapper=document.createElement("div")
wrapper.className="custom-select"

const btn=document.createElement("div")
btn.className="select-btn"

const text=document.createElement("span")
text.textContent=select.options[select.selectedIndex]?.text || "Seleccionar rol"

btn.appendChild(text)

const menu=document.createElement("div")
menu.className="select-options"

Array.from(select.options).forEach(option=>{

const item=document.createElement("div")
item.className="select-option"
item.textContent=option.text

if(option.selected){
item.classList.add("active")
}

item.onclick=function(){

text.textContent=option.text
select.value=option.value

menu.querySelectorAll(".select-option").forEach(o=>{
o.classList.remove("active")
})

item.classList.add("active")

menu.style.display="none"

}

menu.appendChild(item)

})

btn.onclick=function(e){
	e.stopPropagation();
	document.querySelectorAll(".select-options").forEach(m=>{
		if(m!==menu){
 			m.classList.remove("select-options-show");
 			setTimeout(()=>{m.style.display="none";},300);
		}
	});

	// Mostrar el menú
 	if(menu.classList.contains("select-options-show")){
 		menu.classList.remove("select-options-show");
 		setTimeout(()=>{menu.style.display="none";},300);
 		menu.classList.remove("dropup");
 	}else{
		// Mostrar temporalmente para medir
		menu.style.visibility = "hidden";
		menu.style.display = "block";
		menu.classList.remove("dropup");
		menu.style.position = "absolute";
		// Forzar reflow para obtener tamaño real
		const menuRect = menu.getBoundingClientRect();
		const btnRect = btn.getBoundingClientRect();
		const windowHeight = window.innerHeight || document.documentElement.clientHeight;
		const spaceBelow = windowHeight - btnRect.bottom;
		const spaceAbove = btnRect.top;
		// Ocultar de nuevo antes de mostrar correctamente
		menu.style.display = "none";
		menu.style.visibility = "";
		// Ahora mostrar según espacio
		if(spaceBelow < 150 && spaceAbove > spaceBelow){
			// Dropup: usar fixed y posicionar arriba del botón
			menu.classList.add("dropup");
			menu.style.position = "fixed";
			menu.style.left = btnRect.left + "px";
			menu.style.top = (btnRect.top - menuRect.height - 6) + "px";
			menu.style.width = btnRect.width + "px";
		} else {
			// Normal: usar fixed y posicionar debajo del botón
			menu.classList.remove("dropup");
			menu.style.position = "fixed";
			menu.style.left = btnRect.left + "px";
			menu.style.top = (btnRect.bottom + 6) + "px";
			menu.style.width = btnRect.width + "px";
		}
 		menu.style.display = "block";
 		setTimeout(()=>{menu.classList.add("select-options-show");},10);
	}
}

wrapper.appendChild(btn)
wrapper.appendChild(menu)

select.parentNode.insertBefore(wrapper,select)
wrapper.appendChild(select)

})

document.addEventListener("click",function(){
	document.querySelectorAll(".select-options").forEach(menu=>{
 		menu.classList.remove("select-options-show");
 		setTimeout(()=>{
 			menu.style.display="none";
 			menu.style.position = "absolute";
 			menu.style.left = "";
 			menu.style.top = "";
 			menu.style.width = "";
 		},300);
	});
});

})

function toggleError(button) {
			if ( button.className === 'buttinvi2' ) {
				// HIDE ERROR
				button.className = 'buttinvi1';
				element = document.querySelector('.bannerright');
				element.style.right = '-8%';
				document.getElementById('icon').src = 'static/images/icon_eye_closed.svg';
			} else {
				// SHOW ERROR
				button.className = 'buttinvi2';
				element = document.querySelector('.bannerright');
				element.style.right = '0%';
				document.getElementById('icon').src = 'static/images/icon_eye_open.svg';
			}
		}
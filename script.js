
// Countdown Timer for Chakravyuha Event
function updateCountdown() {
	const eventDate = new Date('2025-10-10T00:00:00');
	const now = new Date();
	const diff = eventDate - now;

	if (diff > 0) {
		const days = Math.floor(diff / (1000 * 60 * 60 * 24));
		const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
		const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
		const seconds = Math.floor((diff % (1000 * 60)) / 1000);

		document.getElementById('days').textContent = days.toString().padStart(2, '0');
		document.getElementById('hours').textContent = hours.toString().padStart(2, '0');
		document.getElementById('minutes').textContent = minutes.toString().padStart(2, '0');
		document.getElementById('seconds').textContent = seconds.toString().padStart(2, '0');
	} else {
		document.getElementById('days').textContent = '00';
		document.getElementById('hours').textContent = '00';
		document.getElementById('minutes').textContent = '00';
		document.getElementById('seconds').textContent = '00';
	}
}

setInterval(updateCountdown, 1000);
updateCountdown();

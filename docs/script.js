document.addEventListener('DOMContentLoaded', () => {
    const charger = document.getElementById('drag-charger');
    const port = document.getElementById('target-port');
    const laptopFrame = document.getElementById('laptop-frame');
    const avatarFace = document.querySelector('.avatar-face');
    const batteryStatus = document.querySelector('.battery-status');
    const subtitle = document.getElementById('moan-subtitle');
    const audio = document.getElementById('demo-audio');
    const demoWrapper = document.getElementById('demo');
    const cablePath = document.getElementById('cable-path');
    const previewBtn = document.getElementById('hero-sound-preview-btn');

    let isDragging = false;
    let startX = 0;
    let startY = 0;
    let isConnected = false;

    // Get absolute center of the target port
    function getPortCoords() {
        const rect = port.getBoundingClientRect();
        return {
            x: rect.left + rect.width / 2,
            y: rect.top + rect.height / 2
        };
    }

    // Update dynamic SVG cable line
    function updateCable() {
        const parentRect = demoWrapper.getBoundingClientRect();
        
        // Start point: bottom center of the container
        const startX = parentRect.width / 2;
        const startY = parentRect.height - 25; // 25px offset from bottom
        
        // End point: bottom center of the charger plug
        const chargerLeft = charger.offsetLeft;
        const chargerTop = charger.offsetTop;
        const chargerWidth = charger.offsetWidth;
        const chargerHeight = charger.offsetHeight;
        
        const endX = chargerLeft + chargerWidth / 2;
        const endY = chargerTop + chargerHeight - 5; // offset slightly inside base

        // Calculate distance components
        const dx = endX - startX;
        const dy = endY - startY;
        const distance = Math.hypot(dx, dy);

        // Adjust sag factor based on distance (tighter cable when stretched)
        const sag = Math.max(10, 60 - distance * 0.15);

        // Cubic Bezier control points:
        // cp1 pulls line upwards from outlet
        const cp1x = startX;
        const cp1y = startY - sag * 0.8;
        
        // cp2 pulls line downwards from charger base
        const cp2x = endX;
        const cp2y = endY + sag * 1.5;

        const pathData = `M ${startX} ${startY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${endX} ${endY}`;
        cablePath.setAttribute('d', pathData);
    }

    // Smoothly animate cable path updates during CSS transitions
    function animateCableReset() {
        const startTime = performance.now();
        const duration = 300; // matching CSS transition duration

        function tick(now) {
            const elapsed = now - startTime;
            updateCable();
            if (elapsed < duration) {
                requestAnimationFrame(tick);
            } else {
                updateCable();
            }
        }
        requestAnimationFrame(tick);
    }

    // Spawn a burst of glowing neon particles from the charging port
    function createParticleBurst() {
        const rect = port.getBoundingClientRect();
        const parentRect = demoWrapper.getBoundingClientRect();
        const portX = rect.left - parentRect.left + rect.width / 2;
        const portY = rect.top - parentRect.top + rect.height / 2;

        const emojis = ['❤️', '✨', '⚡', '🥵', '🔥'];

        for (let i = 0; i < 24; i++) {
            const p = document.createElement('div');
            
            // Randomly mix emojis and glowing dots
            if (Math.random() > 0.6) {
                p.className = 'particle emoji-particle';
                p.textContent = emojis[Math.floor(Math.random() * emojis.length)];
            } else {
                p.className = 'particle dot-particle';
                const colors = ['var(--primary)', 'var(--secondary)', 'var(--success)', '#00f6ff', '#ffff00'];
                p.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            }

            demoWrapper.appendChild(p);

            // Angle, speed, and drift velocity
            const angle = Math.random() * Math.PI * 2;
            const speed = 2 + Math.random() * 5;
            const vx = Math.cos(angle) * speed;
            const vy = Math.sin(angle) * speed - 1.5; // slight upward drift

            p.style.left = `${portX}px`;
            p.style.top = `${portY}px`;
            p.style.transform = `translate(-50%, -50%) scale(${0.5 + Math.random() * 0.7})`;

            let posX = portX;
            let posY = portY;
            let opacity = 1.0;
            let scale = 0.5 + Math.random() * 0.7;

            const animate = () => {
                posX += vx;
                posY += vy;
                opacity -= 0.02;
                scale -= 0.01;
                
                p.style.left = `${posX}px`;
                p.style.top = `${posY}px`;
                p.style.opacity = opacity;
                p.style.transform = `translate(-50%, -50%) scale(${Math.max(0, scale)})`;
                
                if (opacity > 0) {
                    requestAnimationFrame(animate);
                } else {
                    p.remove();
                }
            };
            
            requestAnimationFrame(animate);
        }
    }

    // Initialize position tracking
    charger.addEventListener('pointerdown', (e) => {
        if (isConnected) return;
        isDragging = true;
        
        try {
            charger.setPointerCapture(e.pointerId);
        } catch (err) {
            console.warn("Failed to set pointer capture:", err);
        }
        
        const rect = charger.getBoundingClientRect();
        
        // Calculate offset between click point and element top-left
        startX = e.clientX - rect.left;
        startY = e.clientY - rect.top;
        
        charger.style.transition = 'none';
        e.preventDefault(); // Prevent text selection and default drag behaviors
    });

    charger.addEventListener('dragstart', (e) => {
        e.preventDefault(); // Explicitly block default browser dragging
    });


    window.addEventListener('pointermove', (e) => {
        if (!isDragging) return;

        const parentRect = demoWrapper.getBoundingClientRect();
        
        // Calculate new positions relative to parent container
        let newX = e.clientX - parentRect.left - startX;
        let newY = e.clientY - parentRect.top - startY;

        // Constraint checking inside wrapper bounds
        const maxX = parentRect.width - charger.offsetWidth;
        const maxY = parentRect.height - charger.offsetHeight;
        
        newX = Math.max(0, Math.min(newX, maxX));
        newY = Math.max(0, Math.min(newY, maxY));

        // Update positions
        charger.style.left = `${newX}px`;
        charger.style.top = `${newY}px`;
        charger.style.bottom = 'auto';
        charger.style.transform = 'none';

        // Redraw cable curve
        updateCable();

        // Check proximity to target port
        const portCoords = getPortCoords();
        const chargerRect = charger.getBoundingClientRect();
        const chargerTipX = chargerRect.left + chargerRect.width / 2;
        const chargerTipY = chargerRect.top; // Tip is at the top of connector

        const distance = Math.hypot(portCoords.x - chargerTipX, portCoords.y - chargerTipY);

        if (distance < 140) {
            port.classList.add('highlight');
            if (distance < 60) {
                avatarFace.textContent = '🥵';
                avatarFace.style.transform = 'scale(1.25)';
            } else {
                avatarFace.textContent = '😮';
                avatarFace.style.transform = 'scale(1.15)';
            }
        } else {
            port.classList.remove('highlight');
            avatarFace.textContent = '😴';
            avatarFace.style.transform = 'scale(1)';
        }
    });

    window.addEventListener('pointerup', (e) => {
        if (!isDragging) return;
        isDragging = false;
        try {
            charger.releasePointerCapture(e.pointerId);
        } catch (err) {}

        // Check if we dropped it near the port
        const portCoords = getPortCoords();
        const chargerRect = charger.getBoundingClientRect();
        const chargerTipX = chargerRect.left + chargerRect.width / 2;
        const chargerTipY = chargerRect.top;

        const distance = Math.hypot(portCoords.x - chargerTipX, portCoords.y - chargerTipY);

        if (distance < 50) {
            triggerConnection();
        } else {
            resetCharger();
        }
    });

    window.addEventListener('pointercancel', (e) => {
        if (!isDragging) return;
        isDragging = false;
        try {
            charger.releasePointerCapture(e.pointerId);
        } catch (err) {}
        resetCharger();
    });

    charger.addEventListener('lostpointercapture', () => {
        if (isDragging) {
            isDragging = false;
            resetCharger();
        }
    });



    function triggerConnection() {
        isConnected = true;
        port.classList.remove('highlight');
        port.classList.add('connected');
        
        // Snap charger to port coordinates
        const parentRect = demoWrapper.getBoundingClientRect();
        const portRect = port.getBoundingClientRect();
        
        // Calculate position to snap
        const targetLeft = portRect.left - parentRect.left - (charger.offsetWidth / 2) + (port.offsetWidth / 2);
        const targetTop = portRect.top - parentRect.top - 8; // Slight offset so tip goes inside port

        charger.style.transition = 'all 0.2s ease-out';
        charger.style.left = `${targetLeft}px`;
        charger.style.top = `${targetTop}px`;
        charger.style.bottom = 'auto';
        charger.style.transform = 'none';

        // Animate snap path updates
        let startSnap = performance.now();
        const animateSnap = (now) => {
            updateCable();
            if (now - startSnap < 250) {
                requestAnimationFrame(animateSnap);
            }
        };
        requestAnimationFrame(animateSnap);

        // Play the sound!
        audio.currentTime = 0;
        audio.play().catch(err => {
            console.log("Audio play blocked by browser, but event triggered:", err);
        });

        // Trigger animations & state changes
        avatarFace.textContent = '🥵';
        avatarFace.style.transform = 'scale(1.35)';
        batteryStatus.textContent = 'Charging: 100%';
        batteryStatus.style.background = 'rgba(0, 255, 170, 0.15)';
        batteryStatus.style.borderColor = 'var(--success)';
        batteryStatus.style.color = 'var(--success)';

        subtitle.classList.add('show');
        laptopFrame.classList.add('shake');

        // Spawn particle bursts!
        createParticleBurst();

        // Reset after 3.5 seconds
        setTimeout(() => {
            resetState();
        }, 3500);
    }

    function resetCharger() {
        charger.style.transition = 'all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        charger.style.left = 'calc(50% - 30px)';
        charger.style.top = '280px';
        charger.style.bottom = 'auto';
        charger.style.transform = 'none';
        port.classList.remove('highlight');
        
        // Update cable along the reset transition path
        animateCableReset();
    }

    function resetState() {
        isConnected = false;
        port.classList.remove('connected');
        avatarFace.textContent = '😴';
        avatarFace.style.transform = 'scale(1)';
        batteryStatus.textContent = 'Battery Low: 12%';
        batteryStatus.style.background = 'rgba(255, 42, 116, 0.1)';
        batteryStatus.style.borderColor = 'rgba(255, 42, 116, 0.2)';
        batteryStatus.style.color = 'var(--primary)';
        
        subtitle.classList.remove('show');
        laptopFrame.classList.remove('shake');
        
        resetCharger();
    }

    // Sound Preview Event
    if (previewBtn) {
        previewBtn.addEventListener('click', () => {
            audio.currentTime = 0;
            audio.play().catch(err => {
                console.log("Preview audio blocked:", err);
            });

            subtitle.classList.add('show');
            avatarFace.textContent = '🥵';
            avatarFace.style.transform = 'scale(1.3)';
            laptopFrame.classList.add('shake');

            // Burst particle preview
            createParticleBurst();

            setTimeout(() => {
                subtitle.classList.remove('show');
                avatarFace.textContent = '😴';
                avatarFace.style.transform = 'scale(1)';
                laptopFrame.classList.remove('shake');
            }, 3000);
        });
    }

    // Set initial position & redraw cable
    window.addEventListener('resize', updateCable);
    resetCharger();
    setTimeout(updateCable, 100); // safety fallback render
});

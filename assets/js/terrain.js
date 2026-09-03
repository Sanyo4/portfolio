// A live contour terrain behind the hero.
// One plane, displaced by layered noise in the vertex shader; the fragment
// shader draws the contour lines. Cheap enough for a phone.

import * as THREE from 'three';

const canvas = document.getElementById('terrain');
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (canvas && !reduced) {
  const isTouch = window.matchMedia('(hover: none)').matches;
  const dpr = Math.min(window.devicePixelRatio || 1, isTouch ? 1.35 : 1.6);

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(dpr);
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 80);
  camera.position.set(0, 3.4, 9.5);

  const rig = new THREE.Group();
  rig.add(camera);
  scene.add(rig);

  const seg = isTouch ? 150 : 240;
  const geo = new THREE.PlaneGeometry(44, 44, seg, seg);
  geo.rotateX(-Math.PI / 2);

  const uniforms = {
    uTime: { value: 0 },
    uBg: { value: new THREE.Color(0x0d1110) },
    uLine: { value: new THREE.Color(0x9db08c) },
    uLine2: { value: new THREE.Color(0xc7cbc6) },
    uPointer: { value: new THREE.Vector2(0, 0) },
    uLift: { value: 0 },
  };

  const vert = /* glsl */`
    uniform float uTime;
    uniform vec2 uPointer;
    varying float vH;
    varying float vDist;
    varying vec2 vXZ;

    vec3 mod289(vec3 x){return x-floor(x*(1.0/289.0))*289.0;}
    vec2 mod289(vec2 x){return x-floor(x*(1.0/289.0))*289.0;}
    vec3 permute(vec3 x){return mod289(((x*34.0)+1.0)*x);}
    float snoise(vec2 v){
      const vec4 C=vec4(0.211324865405187,0.366025403784439,-0.577350269189626,0.024390243902439);
      vec2 i=floor(v+dot(v,C.yy));
      vec2 x0=v-i+dot(i,C.xx);
      vec2 i1=(x0.x>x0.y)?vec2(1.0,0.0):vec2(0.0,1.0);
      vec4 x12=x0.xyxy+C.xxzz; x12.xy-=i1;
      i=mod289(i);
      vec3 p=permute(permute(i.y+vec3(0.0,i1.y,1.0))+i.x+vec3(0.0,i1.x,1.0));
      vec3 m=max(0.5-vec3(dot(x0,x0),dot(x12.xy,x12.xy),dot(x12.zw,x12.zw)),0.0);
      m=m*m; m=m*m;
      vec3 x=2.0*fract(p*C.www)-1.0;
      vec3 h=abs(x)-0.5;
      vec3 ox=floor(x+0.5);
      vec3 a0=x-ox;
      m*=1.79284291400159-0.85373472095314*(a0*a0+h*h);
      vec3 g;
      g.x=a0.x*x0.x+h.x*x0.y;
      g.yz=a0.yz*x12.xz+h.yz*x12.yw;
      return 130.0*dot(m,g);
    }

    float fbm(vec2 p){
      float a=0.5; float f=0.0;
      for(int i=0;i<5;i++){ f+=a*snoise(p); p=p*2.03+vec2(17.1,9.3); a*=0.5; }
      return f;
    }

    void main(){
      vec3 pos=position;
      vec2 p=pos.xz*0.11;
      float t=uTime*0.045;
      // ridged noise for a mountain feel
      float n=fbm(p+vec2(t*0.6,t*0.35));
      float r=1.0-abs(fbm(p*1.6-vec2(t*0.2,t*0.5)));
      float h=n*1.9+r*r*1.6;
      // sink the middle a touch so the text has a valley
      float valley=exp(-dot(pos.xz*vec2(0.09,0.14),pos.xz*vec2(0.09,0.14)))*1.4;
      h-=valley;
      // pointer lifts the ground gently
      float lift=exp(-dot(pos.xz-uPointer*8.0,pos.xz-uPointer*8.0)*0.06)*0.7;
      h+=lift;
      pos.y=h;
      vH=h;
      vXZ=pos.xz;
      vec4 mv=modelViewMatrix*vec4(pos,1.0);
      vDist=-mv.z;
      gl_Position=projectionMatrix*mv;
    }
  `;

  const frag = /* glsl */`
    precision highp float;
    uniform vec3 uBg;
    uniform vec3 uLine;
    uniform vec3 uLine2;
    uniform float uLift;
    varying float vH;
    varying float vDist;
    varying vec2 vXZ;

    void main(){
      float lvl=vH*3.2;
      float f=fract(lvl);
      float d=min(f,1.0-f);
      float w=fwidth(lvl);
      float line=1.0-smoothstep(0.0,w*1.4,d);
      // every fifth line is brighter
      float major=step(0.8,fract(floor(lvl)/4.0+0.1));
      float fog=smoothstep(40.0,6.0,vDist);
      float edge=smoothstep(22.0,10.0,length(vXZ));
      float alpha=line*fog*edge;
      vec3 col=mix(uLine,uLine2,major*0.55);
      float glow=smoothstep(1.2,2.6,vH)*0.08*fog*edge;
      float a=alpha*(0.5+0.5*major)*0.85+glow;
      if(a<0.004) discard;
      gl_FragColor=vec4(col,a);
    }
  `;

  const applyTheme = () => {
    const light = document.documentElement.getAttribute('data-theme') === 'light';
    uniforms.uLine.value.set(light ? 0x5c7052 : 0x9db08c);
    uniforms.uLine2.value.set(light ? 0x3d4a3a : 0xc7cbc6);
    if (window.__dustMat) window.__dustMat.color.set(light ? 0x5c7052 : 0xc7cbc6);
  };
  window.__terrainTheme = () => applyTheme();

  const mat = new THREE.ShaderMaterial({
    uniforms, vertexShader: vert, fragmentShader: frag,
    transparent: true, depthWrite: false, blending: THREE.NormalBlending,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.y = -1.2;
  scene.add(mesh);

  // dust
  const count = isTouch ? 260 : 520;
  const pts = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    pts[i * 3] = (Math.random() - 0.5) * 36;
    pts[i * 3 + 1] = Math.random() * 6 - 0.5;
    pts[i * 3 + 2] = (Math.random() - 0.5) * 30;
  }
  const pGeo = new THREE.BufferGeometry();
  pGeo.setAttribute('position', new THREE.BufferAttribute(pts, 3));
  const pMat = new THREE.PointsMaterial({ color: 0xc7cbc6, size: 0.035, transparent: true, opacity: 0.5, depthWrite: false, sizeAttenuation: true });
  const dust = new THREE.Points(pGeo, pMat);
  scene.add(dust);
  window.__dustMat = pMat;
  applyTheme();

  // interaction state
  const target = { x: 0, y: 0 };
  const cur = { x: 0, y: 0 };
  let scrollP = 0;
  let visible = true;
  let hasFrame = false;

  function onPointer(e) {
    const x = (e.clientX / window.innerWidth) * 2 - 1;
    const y = (e.clientY / window.innerHeight) * 2 - 1;
    target.x = x; target.y = y;
  }
  window.addEventListener('pointermove', onPointer, { passive: true });
  window.addEventListener('touchmove', (e) => { if (e.touches[0]) onPointer(e.touches[0]); }, { passive: true });

  // Android exposes orientation without a permission prompt; iOS needs a gesture, so it falls back to touch.
  if (isTouch && 'DeviceOrientationEvent' in window && typeof DeviceOrientationEvent.requestPermission !== 'function') {
    window.addEventListener('deviceorientation', (e) => {
      if (e.gamma == null || e.beta == null) return;
      target.x = THREE.MathUtils.clamp(e.gamma / 30, -1, 1);
      target.y = THREE.MathUtils.clamp((e.beta - 45) / 35, -1, 1);
    }, { passive: true });
  }

  function resize() {
    const w = window.innerWidth, h = window.innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.fov = w < 720 ? 52 : 42;
    camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener('resize', resize);

  const hero = document.getElementById('hero');
  if ('IntersectionObserver' in window && hero) {
    new IntersectionObserver((entries) => { visible = entries[0].isIntersecting; }, { threshold: 0 }).observe(hero);
  }
  window.addEventListener('scroll', () => {
    const h = window.innerHeight;
    scrollP = Math.min(1, Math.max(0, window.scrollY / h));
  }, { passive: true });

  const clock = new THREE.Clock();
  function frame() {
    requestAnimationFrame(frame);
    if (!visible) return;
    const t = clock.getElapsedTime();
    uniforms.uTime.value = t;
    cur.x += (target.x - cur.x) * 0.04;
    cur.y += (target.y - cur.y) * 0.04;
    uniforms.uPointer.value.set(cur.x, -cur.y);
    rig.rotation.y = cur.x * 0.08;
    rig.rotation.x = cur.y * 0.04;
    camera.position.y = 3.4 + scrollP * 5.5;
    camera.position.z = 9.5 - scrollP * 2.5;
    camera.lookAt(0, 0.4 - scrollP * 2.0, 0);
    dust.rotation.y = t * 0.01;
    dust.position.y = Math.sin(t * 0.2) * 0.15;
    canvas.style.opacity = String(1 - scrollP * 1.15);
    renderer.render(scene, camera);
    if (!hasFrame) { hasFrame = true; canvas.classList.add('is-ready'); }
  }
  frame();
}

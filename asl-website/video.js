// get term from URL query parameters
const params = new URLSearchParams(window.location.search);
const term = params.get('term');

// load video based on term
const terms = {
    'ARM': './ASL_Videos/arm_rutgers.mp4',
    'BACK': './ASL_Videos/back_rutgers.mp4',
    'CHEST': './ASL_Videos/chest_rutgers.mp4',
    'EARS': './ASL_Videos/ear.mp4',
    'EYES': './ASL_Videos/eyes_rutgers.mp4',
    'HEAD': './ASL_Videos/head_rutgers.mp4',
    'HEART': './ASL_Videos/heart_rutgers.mp4',
    'JAW': './ASL_Videos/jaw_rutgers.mp4',
    'LEGS': './ASL_Videos/legs_rutgers.mp4',
    'LUNGS': './ASL_Videos/lungs_rutgers.mp4',
    'NOSE': './ASL_Videos/nose_rutgers.mp4',
    'RIBS': './ASL_Videos/ribs_rutgers.mp4',
    'STOMACH': './ASL_Videos/stomach_rutgers.mp4',
    'THROAT': './ASL_Videos/throat_rutgers.mp4',
    'WRIST': './ASL_Videos/wrist_rutgers.mp4',
    'SCRAPE': './ASL_Videos/scrape_rutgers.mp4',
    'STAB': './ASL_Videos/stab_rutgers.mp4',
    'STITCH': './ASL_Videos/stitch_rutgers.mp4',
    'CUT': './ASL_Videos/cut_rutgers.mp4',
    'BURN': './ASL_Videos/burn_rutgers.mp4',
    'DIZZY': './ASL_Videos/dizzy_rutgers.mp4',
    'FAINT': './ASL_Videos/faint_rutgers.mp4',
    'HEADACHE': './ASL_Videos/headache_rutgers.mp4',
    'ITCH': './ASL_Videos/itch_rutgers.mp4',
    'STOMACH CRAMPS': './ASL_Videos/stomachcramps_rutgers.mp4',
    'ALCOHOL': './ASL_Videos/alcohol_rutgers.mp4',
    'COCAINE': './ASL_Videos/cocaine_rutgers.mp4',
    'DRUG': './ASL_Videos/drug_rutgers.mp4',
    'MARIJUANA': './ASL_Videos/marijuana_rutgers.mp4',
    'OVERDOSE': './ASL_Videos/overdose_rutgers.mp4'
    
};

if (term && terms[term.toUpperCase()]) {
    document.getElementById('term-title').innerText = term.toUpperCase();
    document.getElementById('term-video').src = terms[term.toUpperCase()];
    console.log("success!");
} else {
    document.getElementById('term-title').innerText = 'Video not found';
    console.log("not found :(");
}
window.Apex = {
  chart: {
    foreColor: '#fff',
    toolbar: {
      show: false
    },
  },
  stroke: {
    width: 3
  },
  dataLabels: {
    enabled: false
  },
  grid: {
    borderColor: "#40475D",
  },
  xaxis: {
    axisTicks: {
      color: '#333'
    },
    axisBorder: {
      color: "#333"
    }
  },
  tooltip: {
    theme: 'dark',
    x: {
      formatter: function (val) {
        return moment(new Date(val)).format("HH:mm:ss")
      }
    }
  },
  yaxis: {
    decimalsInFloat: 2,
    opposite: true,
    labels: {
      offsetX: -10
    }
  }
};

function makeFactionsChart(element) {
  var options = {
    series: [axiomCount, bravosCount, lyraCount, munaCount, ordisCount, yzmirCount],
    labels: ['Axiom', 'Bravos', 'Lyra', 'Muna', 'Ordis', 'Yzmir'],
    colors: ['rgb(140, 67, 42)', 'rgb(195, 38, 55)', 'rgb(207, 65, 113)', 'rgb(61, 107, 66)', 'rgb(15, 101, 147)', 'rgb(118, 72, 145)'],
    legend: {
      show: true,
      position: 'bottom',
    },
    chart: {
      width: 380,
      type: 'pie',
      animations: {
        enabled: false
      },
      toolbar: {
        show: false
      },
      zoom: {
        enabled: false
      }
    },
    stroke: {
        width: 0,
    },
    title: {
      text: 'Factions',
      style: {
        fontSize: '20pt',
      },
      align: 'center',
    },
  };

  var chart = new ApexCharts(element, options);
  chart.render();
}

function makeRaritiesChart(element) {
  var options = {
    series: [commonCount, rareCount, uniqueCount],
    labels: ['Common', 'Rare', 'Unique'],
    colors: ['rgb(190, 190, 190)', 'rgb(0, 102, 255)', 'rgb(255, 215, 0)'],
    legend: {
      show: true,
      position: 'bottom',
    },
    chart: {
      width: 380,
      type: 'pie',
      animations: {
        enabled: false
      },
      toolbar: {
        show: false
      },
      zoom: {
        enabled: false
      }
    },
    stroke: {
        width: 0,
    },
    title: {
      text: 'Rarities',
      style: {
        fontSize: '20pt',
      },
      align: 'center',
    },
  };

  var chart = new ApexCharts(element, options);
  chart.render();
}

function makeTypesChart(element) {
  var options = {
    series: [heroCount, characterCount, spellCount, landmarkCount],
    labels: ['Hero', 'Character', 'Spell', 'Landmark'],
    legend: {
      show: true,
      position: 'bottom',
    },
    chart: {
      width: 380,
      type: 'pie',
      animations: {
        enabled: false
      },
      toolbar: {
        show: false
      },
      zoom: {
        enabled: false
      }
    },
    stroke: {
        width: 0,
    },
    title: {
      text: 'Types',
      style: {
        fontSize: '20pt',
      },
      align: 'center',
    },
  };

  var chart = new ApexCharts(element, options);
  chart.render();
}


// Parse the cards gathering stats
var axiomCount = 0;
var bravosCount = 0;
var lyraCount = 0;
var munaCount = 0;
var ordisCount = 0;
var yzmirCount = 0;

var commonCount = 0;
var rareCount = 0;
var uniqueCount = 0;

var collectionCount = 0;
var knownCardsCount = 0;
var differentCardsCount = 0;

var heroCount = 0;
var characterCount = 0;
var spellCount = 0;
var landmarkCount = 0;
var foilerCount = 0;
var unknownTypeCount = 0;

Object.values(cards).forEach(card => {
  // Skip foilers
  if (card.type == "FOILER") {
    return;
  }

  var count = card.inMyCollection;
  knownCardsCount++;
  collectionCount += count;
  if (count > 0) {
    differentCardsCount++;
  }

  switch (card.mainFaction) {
    case "AX":
      axiomCount += count;
      break;
    case "BR":
      bravosCount += count;
      break;
    case "LY":
      lyraCount += count;
      break;
    case "MU":
      munaCount += count;
      break;
    case "OR":
      ordisCount += count;
      break;
    case "YZ":
      yzmirCount += count;
      break;
  }

  switch (card.rarity) {
    case "COMMON":
      commonCount += count
      break;
    case "RARE":
      rareCount += count;
      break;
    case "UNIQUE":
      uniqueCount += count;
      break;
  }

  switch (card.type) {
    case "HERO":
      heroCount += count;
      break;
    case "CHARACTER":
      characterCount += count;
      break;
    case "SPELL":
      spellCount += count;
      break;
    case "PERMANENT":
      landmarkCount += count;
      break;
    case "FOILER":
      foilerCount += count;
      break;
    default:
      unknownTypeCount += count;
      break;
  }
});

console.log(`Collection count: ${collectionCount}`)
console.log(`Kown cards count: ${knownCardsCount}`)
console.log(`Different cards count: ${differentCardsCount}`)

makeFactionsChart(document.querySelector('#factions'));
makeRaritiesChart(document.querySelector('#rarities'));
makeTypesChart(document.querySelector('#types'));
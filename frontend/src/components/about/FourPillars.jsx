import { ArrowLeft, Heart, Star, Coins, Lotus } from 'lucide-react';
import { Link } from 'react-router-dom';

const FourPillars = () => {
  const pillars = [
    {
      name: "Clarity",
      icon: Star,
      color: "blue",
      description: "Illuminating life's path with divine wisdom",
      details: [
        "Clear decision-making in complex situations",
        "Understanding your life purpose and dharma",
        "Overcoming confusion and mental fog",
        "Gaining insight into life patterns and cycles"
      ],
      quote: "When the mind is clear, the path becomes visible."
    },
    {
      name: "Love", 
      icon: Heart,
      color: "pink",
      description: "Harmonizing relationships and opening the heart",
      details: [
        "Healing relationship conflicts and misunderstandings",
        "Attracting and maintaining loving partnerships",
        "Improving family dynamics and communication",
        "Developing self-love and compassion"
      ],
      quote: "Love is the bridge between two hearts and the path to the divine."
    },
    {
      name: "Prosperity",
      icon: Coins,
      color: "yellow", 
      description: "Manifesting abundance in all areas of life",
      details: [
        "Career advancement and professional success",
        "Financial abundance and wealth creation",
        "Business growth and entrepreneurial guidance",
        "Removing blocks to prosperity consciousness"
      ],
      quote: "True prosperity flows when we align with our highest purpose."
    },
    {
      name: "Enlightenment",
      icon: Lotus,
      color: "purple",
      description: "Awakening to your highest spiritual potential",
      details: [
        "Deep meditation and spiritual practices",
        "Understanding cosmic consciousness",
        "Transcending ego limitations",
        "Experiencing unity with the divine"
      ],
      quote: "Enlightenment is not a destination, but a way of being."
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: {
        bg: "from-blue-50 to-indigo-50",
        border: "border-blue-200",
        icon: "text-blue-600",
        text: "text-blue-800",
        button: "bg-blue-600 hover:bg-blue-700"
      },
      pink: {
        bg: "from-pink-50 to-rose-50", 
        border: "border-pink-200",
        icon: "text-pink-600",
        text: "text-pink-800",
        button: "bg-pink-600 hover:bg-pink-700"
      },
      yellow: {
        bg: "from-yellow-50 to-orange-50",
        border: "border-yellow-200", 
        icon: "text-yellow-600",
        text: "text-yellow-800",
        button: "bg-yellow-600 hover:bg-yellow-700"
      },
      purple: {
        bg: "from-purple-50 to-indigo-50",
        border: "border-purple-200",
        icon: "text-purple-600", 
        text: "text-purple-800",
        button: "bg-purple-600 hover:bg-purple-700"
      }
    };
    return colors[color];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-yellow-50 to-orange-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-600 to-yellow-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <Link to="/" className="inline-flex items-center text-orange-100 hover:text-white mb-6">
            <ArrowLeft className="h-5 w-5 mr-2" />
            Back to Home
          </Link>
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-4">
              The Four Sacred Pillars
            </h1>
            <p className="text-xl md:text-2xl text-orange-100 max-w-3xl mx-auto">
              The Foundation of Complete Spiritual Transformation
            </p>
          </div>
        </div>
      </div>

      {/* Introduction */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-white rounded-xl p-8 shadow-lg border border-orange-200 mb-16">
          <p className="text-lg text-gray-700 leading-relaxed mb-6">
            For over 1000 years, the Jyotirananthan lineage has recognized that true spiritual transformation rests upon four sacred pillars. These are not separate paths, but interconnected aspects of a complete spiritual life.
          </p>
          <p className="text-lg text-gray-700 leading-relaxed">
            Swami Jyotirananthan's guidance addresses all four pillars, ensuring that seekers experience holistic growth and lasting transformation in every area of their lives.
          </p>
        </div>

        {/* Pillars */}
        <div className="space-y-16">
          {pillars.map((pillar, index) => {
            const colors = getColorClasses(pillar.color);
            const IconComponent = pillar.icon;
            
            return (
              <div key={pillar.name} className={`bg-gradient-to-br ${colors.bg} rounded-xl p-8 shadow-lg border ${colors.border}`}>
                <div className="flex items-center mb-6">
                  <div className={`bg-white rounded-full p-3 mr-4 shadow-md`}>
                    <IconComponent className={`h-8 w-8 ${colors.icon}`} />
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold text-gray-900">{pillar.name}</h2>
                    <p className={`text-lg ${colors.text}`}>{pillar.description}</p>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-4">Areas of Guidance</h3>
                    <ul className="space-y-2">
                      {pillar.details.map((detail, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className={`${colors.icon} mr-2 mt-1`}>•</span>
                          <span className="text-gray-700">{detail}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="flex flex-col justify-center">
                    <div className="bg-white/70 rounded-lg p-6 border-l-4 border-gray-300">
                      <p className={`${colors.text} italic text-lg mb-2`}>"{pillar.quote}"</p>
                      <p className="text-sm text-gray-600">- Swami Jyotirananthan</p>
                    </div>
                    
                    <Link 
                      to="/spiritual-guidance"
                      className={`${colors.button} text-white px-6 py-3 rounded-lg font-semibold text-center mt-4 transition-colors`}
                    >
                      Explore {pillar.name} Guidance
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Integration */}
        <div className="bg-gradient-to-br from-orange-600 to-yellow-600 rounded-xl p-8 text-white mt-16">
          <h2 className="text-3xl font-bold mb-6 text-center">The Integrated Path</h2>
          <p className="text-xl leading-relaxed mb-6 text-center">
            True spiritual mastery comes not from focusing on one pillar alone, but from harmoniously developing all four aspects of your being. Swamiji's guidance ensures balanced growth across all dimensions of your life.
          </p>
          
          <div className="grid md:grid-cols-4 gap-4 mt-8">
            {pillars.map((pillar) => {
              const IconComponent = pillar.icon;
              return (
                <div key={pillar.name} className="text-center">
                  <div className="bg-white/20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
                    <IconComponent className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="font-semibold">{pillar.name}</h3>
                </div>
              );
            })}
          </div>
          
          <div className="text-center mt-8">
            <Link 
              to="/spiritual-guidance" 
              className="inline-flex items-center bg-white text-orange-600 px-8 py-3 rounded-full font-semibold hover:bg-orange-50 transition-colors"
            >
              Begin Your Complete Transformation
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FourPillars;
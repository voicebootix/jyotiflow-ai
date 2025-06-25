import { ArrowLeft, BookOpen, Star, Scroll ,BUILDING2 } from 'lucide-react';
import { Link } from 'react-router-dom';

const TamilHeritage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <Link to="/" className="inline-flex items-center text-red-100 hover:text-white mb-6">
            <ArrowLeft className="h-5 w-5 mr-2" />
            Back to Home
          </Link>
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-4">
              Tamil Spiritual Heritage
            </h1>
            <p className="text-xl md:text-2xl text-red-100 max-w-3xl mx-auto">
              Ancient Wisdom from the Land of Temples and Saints
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        
        {/* Introduction */}
        <section className="mb-16">
          <div className="bg-white rounded-xl p-8 shadow-lg border border-orange-200">
            <p className="text-lg text-gray-700 leading-relaxed mb-6">
              Tamil Nadu, the land of ancient temples and enlightened saints, has been a beacon of spiritual wisdom for over 2000 years. From the mystical poetry of the Alvars and Nayanars to the profound philosophy of great sages, this sacred land has given birth to some of humanity's most profound spiritual insights.
            </p>
            
            <p className="text-lg text-gray-700 leading-relaxed">
              Swami Jyotirananthan carries forward this magnificent heritage, bringing the timeless wisdom of Tamil spiritual tradition to seekers worldwide through the medium of modern technology.
            </p>
          </div>
        </section>

        {/* Ancient Traditions */}
        <section className="mb-16">
          <div className="flex items-center mb-8">
            <Temple className="h-8 w-8 text-red-600 mr-3" />
            <h2 className="text-3xl font-bold text-gray-900">Ancient Traditions</h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white rounded-xl p-6 shadow-lg border border-red-200">
              <div className="flex items-center mb-4">
                <Star className="h-6 w-6 text-yellow-600 mr-3" />
                <h3 className="text-xl font-semibold text-gray-900">Tamil Jyotish</h3>
              </div>
              <p className="text-gray-700 mb-4">
                The ancient science of Tamil astrology, refined over millennia, offers profound insights into life patterns, karmic influences, and optimal timing for important decisions.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Rasi and Navamsa chart analysis</li>
                <li>• Dasha and transit predictions</li>
                <li>• Compatibility and muhurta selection</li>
                <li>• Remedial measures and gemstone guidance</li>
              </ul>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-lg border border-red-200">
              <div className="flex items-center mb-4">
                <BookOpen className="h-6 w-6 text-blue-600 mr-3" />
                <h3 className="text-xl font-semibold text-gray-900">Sacred Literature</h3>
              </div>
              <p className="text-gray-700 mb-4">
                Tamil spiritual literature, including the Tirukkural, Divya Prabandham, and Tevaram, contains profound wisdom on ethics, devotion, and the path to liberation.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Thiruvalluvar's ethical teachings</li>
                <li>• Devotional poetry of the saints</li>
                <li>• Philosophical treatises on consciousness</li>
                <li>• Practical guidance for daily life</li>
              </ul>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-lg border border-red-200">
              <div className="flex items-center mb-4">
                <Scroll className="h-6 w-6 text-green-600 mr-3" />
                <h3 className="text-xl font-semibold text-gray-900">Mantra Tradition</h3>
              </div>
              <p className="text-gray-700 mb-4">
                Sacred sound formulas passed down through generations, each mantra carrying specific vibrational frequencies for healing, protection, and spiritual awakening.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Deity-specific mantras for various purposes</li>
                <li>• Healing mantras for physical and emotional wellness</li>
                <li>• Protection mantras for spiritual safety</li>
                <li>• Meditation mantras for consciousness expansion</li>
              </ul>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-lg border border-red-200">
              <div className="flex items-center mb-4">
                <BUILDING2 className="h-6 w-6 text-purple-600 mr-3" />
                <h3 className="text-xl font-semibold text-gray-900">Temple Science</h3>
              </div>
              <p className="text-gray-700 mb-4">
                Tamil temples are not just places of worship but sophisticated spiritual technologies designed to enhance consciousness and facilitate divine connection.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Sacred geometry and energy patterns</li>
                <li>• Ritual practices for spiritual purification</li>
                <li>• Festival cycles aligned with cosmic rhythms</li>
                <li>• Community gathering and collective consciousness</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Great Saints */}
        <section className="mb-16">
          <div className="flex items-center mb-8">
            <Star className="h-8 w-8 text-red-600 mr-3" />
            <h2 className="text-3xl font-bold text-gray-900">Lineage of Great Saints</h2>
          </div>
          
          <div className="bg-white rounded-xl p-8 shadow-lg border border-red-200">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="bg-red-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🙏</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Thiruvalluvar</h3>
                <p className="text-sm text-gray-600">
                  Author of Tirukkural, the universal code of ethics and righteous living that guides moral conduct.
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-orange-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🎵</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Appar & Sambandar</h3>
                <p className="text-sm text-gray-600">
                  Great Shaivite saints whose devotional hymns express the ecstasy of divine love and surrender.
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-yellow-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">💝</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Andal & Alvars</h3>
                <p className="text-sm text-gray-600">
                  Vaishnavite poet-saints who sang of divine love and the path of complete surrender to the Supreme.
                </p>
              </div>
            </div>
            
            <div className="mt-8 bg-red-50 rounded-lg p-6 border-l-4 border-red-400">
              <p className="text-red-800 italic text-center">
                "The wisdom of these great souls flows through the Jyotirananthan lineage, preserved and transmitted through generations of spiritual masters."
              </p>
              <p className="text-sm text-red-600 mt-2 text-center">- Swami Jyotirananthan</p>
            </div>
          </div>
        </section>

        {/* Modern Application */}
        <section className="mb-16">
          <div className="flex items-center mb-8">
            <BookOpen className="h-8 w-8 text-red-600 mr-3" />
            <h2 className="text-3xl font-bold text-gray-900">Ancient Wisdom for Modern Life</h2>
          </div>
          
          <div className="bg-white rounded-xl p-8 shadow-lg border border-red-200">
            <p className="text-lg text-gray-700 leading-relaxed mb-6">
              While rooted in ancient tradition, Tamil spiritual wisdom is remarkably relevant to contemporary challenges. Swami Jyotirananthan skillfully applies these timeless principles to modern situations:
            </p>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Career & Success</h4>
                <ul className="space-y-2 text-gray-700">
                  <li>• Dharmic approach to professional life</li>
                  <li>• Timing career moves with astrological guidance</li>
                  <li>• Balancing ambition with spiritual values</li>
                  <li>• Finding purpose beyond material success</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Relationships & Family</h4>
                <ul className="space-y-2 text-gray-700">
                  <li>• Traditional wisdom for modern relationships</li>
                  <li>• Compatibility analysis using ancient methods</li>
                  <li>• Healing family conflicts with compassion</li>
                  <li>• Raising children with spiritual values</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section>
          <div className="bg-gradient-to-br from-red-600 to-orange-600 rounded-xl p-8 text-white">
            <h2 className="text-3xl font-bold mb-6 text-center">Experience the Heritage</h2>
            <p className="text-xl leading-relaxed mb-6 text-center">
              Connect with the profound wisdom of Tamil spiritual tradition through Swami Jyotirananthan's guidance. Experience how ancient insights can transform your modern life.
            </p>
            
            <div className="text-center">
              <Link 
                to="/spiritual-guidance" 
                className="inline-flex items-center bg-white text-red-600 px-8 py-3 rounded-full font-semibold hover:bg-red-50 transition-colors"
              >
                Explore Tamil Wisdom
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default TamilHeritage;
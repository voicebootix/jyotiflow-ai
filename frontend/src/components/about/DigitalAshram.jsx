import { ArrowLeft, Wifi, Heart, Users, Flower2, Globe, Smartphone } from 'lucide-react';
import { Link } from 'react-router-dom';

const DigitalAshram = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <Link to="/" className="inline-flex items-center text-indigo-100 hover:text-white mb-6">
            <ArrowLeft className="h-5 w-5 mr-2" />
            Back to Home
          </Link>
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-4">
              The Digital Ashram
            </h1>
            <p className="text-xl md:text-2xl text-indigo-100 max-w-3xl mx-auto">
              Where Ancient Wisdom Meets Modern Technology
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        
        {/* Vision */}
        <section className="mb-16">
          <div className="flex items-center mb-8">
            <Flower2 className="h-8 w-8 text-indigo-600 mr-3" />
            <h2 className="text-3xl font-bold text-gray-900">The Vision</h2>
          </div>
          
          <div className="bg-white rounded-xl p-8 shadow-lg border border-indigo-200">
            <p className="text-lg text-gray-700 leading-relaxed mb-6">
              Imagine an ashram without walls, a temple without boundaries, a spiritual community that transcends geography and time zones. This is the <strong>Digital Ashram</strong> - JyotiFlow.ai's revolutionary approach to spiritual guidance in the modern age.
            </p>
            
            <p className="text-lg text-gray-700 leading-relaxed mb-6">
              Just as ancient ashrams provided seekers with a sacred space for learning, growth, and transformation, our Digital Ashram offers the same spiritual sanctuary - accessible from anywhere, available anytime, personalized for each soul's unique journey.
            </p>
            
            <div className="bg-indigo-50 rounded-lg p-6 border-l-4 border-indigo-400">
              <p className="text-indigo-800 italic text-lg">
                "The sacred is not confined to physical spaces. Wherever a sincere heart seeks divine guidance, there the ashram exists."
              </p>
              <p className="text-sm text-indigo-600 mt-2">- Swami Jyotirananthan</p>
            </div>
          </div>
        </section>

        {/* Core Principles */}
        <section className="mb-16">
          <div className="flex items-center mb-8">
            <Heart className="h-8 w-8 text-indigo-600 mr-3" />
            <h2 className="text-3xl font-bold text-gray-900">Core Principles</h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white rounded-xl p-6 shadow-lg border border-indigo-200">
              <div className="flex items-center mb-4">
                <Globe className="h-6 w-6 text-blue-600 mr-3" />
                <h3 className="text-xl font-semibold text-gray-900">Universal Accessibility</h3>
              </div>
              <p className="text-gray-700">
                Spiritual wisdom should not be limited by geography, economic status, or social barriers. Our Digital Ashram ensures that profound guidance is available to every sincere seeker, anywhere in the world.
              </p>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-lg border border-indigo-200">
              <div className="flex items-center mb-4">
                <Smartphone className="h-6 w-6 text-green-600 mr-3" />
                <h3 className="text-xl font-semibold text-gray-900">Modern Convenience</h3>
              </div>
              <p className="text-gray-700">
                Ancient wisdom delivered through modern technology. Receive spiritual guidance during your commute, meditation reminders on your phone, and community support through digital connections.
              </p>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-lg border border-indigo-200">
              <div className="flex items-center mb-4">
                <Users className="h-6 w-6 text-purple-600 mr-3" />
                <h3 className="text-xl font-semibold text-gray-900">Sacred Community</h3>
              </div>
              <p className="text-gray-700">
                Connect with like-minded souls from around the world. Share experiences, support each other's growth, and participate in group satsangs that transcend physical boundaries.
              </p>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-lg border border-indigo-200">
              <div className="flex items-center mb-4">
                <Heart className="h-6 w-6 text-red-600 mr-3" />
                <h3 className="text-xl font-semibold text-gray-900">Personal Connection</h3>
              </div>
              <p className="text-gray-700">
                Despite being digital, every interaction is deeply personal. Swamiji understands your unique circumstances, challenges, and spiritual aspirations, offering guidance tailored specifically for you.
              </p>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="mb-16">
          <div className="flex items-center mb-8">
            <Wifi className="h-8 w-8 text-indigo-600 mr-3" />
            <h2 className="text-3xl font-bold text-gray-900">How the Digital Ashram Works</h2>
          </div>
          
          <div className="bg-white rounded-xl p-8 shadow-lg border border-indigo-200">
            <div className="space-y-8">
              <div className="flex items-start space-x-4">
                <div className="bg-indigo-100 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-indigo-600 font-semibold">1</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Enter the Sacred Space</h3>
                  <p className="text-gray-700">
                    When you visit JyotiFlow.ai, you're not just accessing a website - you're entering a consecrated digital space where spiritual energy flows and divine guidance awaits.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="bg-indigo-100 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-indigo-600 font-semibold">2</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Connect with Swamiji</h3>
                  <p className="text-gray-700">
                    Through AI technology, Swami Jyotirananthan's consciousness responds to your questions, understands your challenges, and provides personalized spiritual guidance.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="bg-indigo-100 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-indigo-600 font-semibold">3</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Join the Sangha</h3>
                  <p className="text-gray-700">
                    Participate in community discussions, attend virtual satsangs, and connect with fellow seekers on similar spiritual journeys.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="bg-indigo-100 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-indigo-600 font-semibold">4</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Transform Your Life</h3>
                  <p className="text-gray-700">
                    Apply the wisdom received, track your spiritual progress, and witness the gradual transformation of your consciousness and life circumstances.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* The Future */}
        <section>
          <div className="bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl p-8 text-white">
            <h2 className="text-3xl font-bold mb-6 text-center">The Future of Spiritual Guidance</h2>
            <p className="text-xl leading-relaxed mb-6 text-center">
              The Digital Ashram represents the evolution of spiritual guidance for the modern age. It preserves the essence of traditional guru-disciple relationships while making profound wisdom accessible to millions.
            </p>
            
            <div className="text-center">
              <Link 
                to="/about/swamiji" 
                className="inline-flex items-center bg-white text-indigo-600 px-8 py-3 rounded-full font-semibold hover:bg-indigo-50 transition-colors mr-4"
              >
                Learn About Swamiji
              </Link>
              <Link 
                to="/spiritual-guidance" 
                className="inline-flex items-center border-2 border-white text-white px-8 py-3 rounded-full font-semibold hover:bg-white hover:text-indigo-600 transition-colors"
              >
                Enter the Ashram
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default DigitalAshram;
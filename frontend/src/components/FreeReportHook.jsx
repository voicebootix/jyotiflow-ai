import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Card, 
  CardContent 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Star, Check, Gift, ArrowRight } from "lucide-react";

const FreeReportHook = ({ 
  showButton = true, 
  buttonText = "Get Your FREE Report Now",
  onButtonClick = null,
  size = 'default' // 'small', 'default', 'large'
}) => {
  const navigate = useNavigate();
  
  const handleButtonClick = () => {
    if (onButtonClick) {
      onButtonClick();
    } else {
      // Use React Router navigation instead of window.location.href
      navigate('/register');
    }
  };
  
  const getSizeClasses = () => {
    switch(size) {
      case 'small':
        return {
          card: 'py-4',
          title: 'text-lg font-bold',
          subtitle: 'text-base',
          features: 'text-xs',
          badge: 'text-sm px-3 py-1'
        };
      case 'large':
        return {
          card: 'py-8',
          title: 'text-2xl font-bold',
          subtitle: 'text-xl',
          features: 'text-base',
          badge: 'text-lg px-6 py-3'
        };
      default:
        return {
          card: 'py-6',
          title: 'text-xl font-bold',
          subtitle: 'text-lg',
          features: 'text-sm',
          badge: 'text-base px-4 py-2'
        };
    }
  };

  const classes = getSizeClasses();

  return (
    <Card className="bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-200 shadow-lg hover:shadow-xl transition-shadow">
      <CardContent className={`text-center ${classes.card}`}>
        <div className="flex flex-col items-center space-y-3">
          {/* Main Hook Line */}
          <div className="flex items-center gap-2 text-orange-800">
            <Star className="w-6 h-6 text-yellow-500" />
            <h3 className={classes.title}>
              Get Your Complete Spiritual Report & Personal Reading from Swami Jyotirananthan
            </h3>
            <Star className="w-6 h-6 text-yellow-500" />
          </div>
          
          {/* Compelling CTA */}
          <p className={`${classes.subtitle} text-orange-700 font-semibold`}>
            Just Sign Up and You Get That FREE! 
          </p>
          
          {/* Value Points */}
          <div className={`flex flex-wrap justify-center gap-4 ${classes.features} text-orange-600 mt-2`}>
            <div className="flex items-center gap-1">
              <Check className="w-4 h-4 text-green-600" />
              <span>Complete Vedic Birth Chart</span>
            </div>
            <div className="flex items-center gap-1">
              <Check className="w-4 h-4 text-green-600" />
              <span>Personal AI Reading by Swamiji</span>
            </div>
            <div className="flex items-center gap-1">
              <Check className="w-4 h-4 text-green-600" />
              <span>Spiritual Guidance & Remedies</span>
            </div>
            <div className="flex items-center gap-1">
              <Check className="w-4 h-4 text-green-600" />
              <span>Worth $60-105 USD</span>
            </div>
          </div>
          
          {/* Free Badge */}
          <Badge className={`bg-orange-100 text-orange-800 ${classes.badge} font-bold`}>
            <Gift className="w-4 h-4 mr-1" />
            100% FREE - No Credit Card Required
          </Badge>
          
          {/* Call to Action Button */}
          {showButton && (
            <Button 
              onClick={handleButtonClick}
              className="bg-orange-600 hover:bg-orange-700 text-white font-bold px-8 py-3 text-lg shadow-lg hover:shadow-xl transition-all"
              size="lg"
            >
              {buttonText}
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default FreeReportHook;
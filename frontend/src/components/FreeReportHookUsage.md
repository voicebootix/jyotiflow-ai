# Free Report Hook Component - Usage Guide

## Overview
The `FreeReportHook` component is a powerful conversion tool that can be placed throughout your site to drive users to register for their free birth chart and AI reading from Swami Jyotirananthan.

## Key Hook Message
**"Get Your Complete Spiritual Report & Personal Reading from Swami Jyotirananthan - Just Sign Up and You Get That FREE!"**

## Component Props

```jsx
<FreeReportHook 
  showButton={true}              // Show/hide the CTA button
  buttonText="Get Your FREE Report Now"  // Customize button text
  onButtonClick={() => {...}}   // Custom click handler
  size="default"                 // 'small', 'default', 'large'
/>
```

## Usage Examples

### 1. Homepage Hero Section (Large)
```jsx
import FreeReportHook from '@/components/FreeReportHook';

const HomePage = () => {
  return (
    <div>
      {/* Other content */}
      <FreeReportHook 
        size="large"
        buttonText="Start Your Spiritual Journey FREE"
        onButtonClick={() => window.location.href = '/register'}
      />
    </div>
  );
};
```

### 2. Blog Post Footer (Default)
```jsx
const BlogPost = () => {
  return (
    <article>
      {/* Blog content */}
      <FreeReportHook 
        buttonText="Get Your Personal Reading Now"
      />
    </article>
  );
};
```

### 3. Sidebar Widget (Small)
```jsx
const Sidebar = () => {
  return (
    <aside>
      {/* Other sidebar content */}
      <FreeReportHook 
        size="small"
        buttonText="Free Report"
      />
    </aside>
  );
};
```

### 4. Exit Intent Popup (Default)
```jsx
const ExitIntentModal = ({ isOpen, onClose }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="p-6">
        <h2 className="text-xl mb-4">Wait! Don't Leave Empty-Handed</h2>
        <FreeReportHook 
          buttonText="Get My FREE Report Before I Go"
          onButtonClick={() => {
            window.location.href = '/register';
            onClose();
          }}
        />
      </div>
    </Modal>
  );
};
```

### 5. About Swamiji Page (Large)
```jsx
const AboutSwamiji = () => {
  return (
    <div>
      {/* Swamiji bio and credentials */}
      <div className="mt-8">
        <FreeReportHook 
          size="large"
          buttonText="Experience Swamiji's Wisdom FREE"
        />
      </div>
    </div>
  );
};
```

### 6. Footer Section (Small)
```jsx
const Footer = () => {
  return (
    <footer>
      {/* Footer links */}
      <div className="mt-6 border-t pt-6">
        <FreeReportHook 
          size="small"
          showButton={false}  // Just show the value prop
        />
      </div>
    </footer>
  );
};
```

### 7. After Viewing Services (Default)
```jsx
const ServicesPage = () => {
  return (
    <div>
      {/* Services content */}
      <div className="mt-8 p-6 bg-gray-50 rounded-lg">
        <h3 className="text-xl mb-4">Try Before You Buy</h3>
        <FreeReportHook 
          buttonText="Get Free Sample Reading"
        />
      </div>
    </div>
  );
};
```

### 8. Mobile Sticky Bottom (Small)
```jsx
const MobileStickyHook = () => {
  const [isVisible, setIsVisible] = useState(true);

  return (
    <>
      {isVisible && (
        <div className="fixed bottom-0 left-0 right-0 z-50 md:hidden bg-white shadow-lg border-t">
          <div className="p-2">
            <FreeReportHook 
              size="small"
              buttonText="FREE Report"
              onButtonClick={() => window.location.href = '/register'}
            />
            <button 
              onClick={() => setIsVisible(false)}
              className="absolute top-1 right-1 text-gray-400"
            >
              ×
            </button>
          </div>
        </div>
      )}
    </>
  );
};
```

## Strategic Placement Locations

### High-Converting Placements
1. **Homepage Hero** - First thing users see
2. **Blog Post Endings** - After valuable content consumption
3. **About Swamiji Page** - After building credibility
4. **Service Pages** - When users are considering options
5. **Exit Intent** - Last chance to convert

### Supporting Placements
1. **Footer** - Always visible
2. **Sidebar** - Constant presence
3. **Mobile Sticky** - Mobile users
4. **Thank You Pages** - After other actions
5. **404 Pages** - Turn bounce into conversion

## Conversion Optimization Tips

### 1. A/B Testing Different Messaging
```jsx
const getRandomButtonText = () => {
  const options = [
    "Get Your FREE Report Now",
    "Start Your Spiritual Journey FREE",
    "Experience Swamiji's Wisdom FREE",
    "Get My Personal Reading FREE",
    "Discover Your Destiny FREE"
  ];
  return options[Math.floor(Math.random() * options.length)];
};

<FreeReportHook buttonText={getRandomButtonText()} />
```

### 2. Time-Based Urgency
```jsx
const getTodayMessage = () => {
  const day = new Date().getDay();
  const messages = {
    0: "Sunday Special: Free Spiritual Reading",
    1: "Monday Motivation: Free Birth Chart",
    2: "Tuesday Transformation: Free Reading",
    // ... etc
  };
  return messages[day] || "Get Your FREE Report Now";
};
```

### 3. Personalization Based on User Behavior
```jsx
const getPersonalizedHook = (userBehavior) => {
  if (userBehavior.viewedServices) {
    return {
      buttonText: "Try Before You Buy - FREE",
      size: "large"
    };
  } else if (userBehavior.readBlog) {
    return {
      buttonText: "Get Your Personal Reading",
      size: "default"
    };
  }
  return { buttonText: "Get Your FREE Report Now", size: "default" };
};
```

## Analytics Tracking

### Track Hook Performance
```jsx
const FreeReportHookWithTracking = (props) => {
  const handleClick = () => {
    // Track conversion attempt
    gtag('event', 'free_report_hook_click', {
      'location': props.location || 'unknown',
      'button_text': props.buttonText,
      'size': props.size
    });
    
    // Original click handler
    if (props.onButtonClick) {
      props.onButtonClick();
    }
  };

  return (
    <FreeReportHook 
      {...props}
      onButtonClick={handleClick}
    />
  );
};
```

## Best Practices

### 1. Don't Overwhelm
- Use maximum 2-3 hooks per page
- Vary the sizes and placements
- Space them out appropriately

### 2. Context Matters
- Match button text to page context
- Use appropriate sizing for placement
- Consider user journey stage

### 3. Mobile Optimization
- Use smaller sizes on mobile
- Consider sticky placement
- Ensure touch-friendly buttons

### 4. Performance
- Lazy load hooks below the fold
- Optimize images and animations
- Monitor page load impact

## Expected Results

### Conversion Rates by Placement
- **Homepage Hero**: 8-15% click rate
- **Blog Post Footer**: 5-12% click rate
- **Exit Intent**: 15-25% click rate
- **Sidebar**: 2-5% click rate
- **Mobile Sticky**: 10-18% click rate

### Key Success Metrics
- **Click-through Rate**: % who click the hook
- **Registration Rate**: % who complete signup
- **Value Realization**: % who view their report
- **Premium Conversion**: % who upgrade after free report

## Implementation Checklist

- [ ] Add FreeReportHook to homepage hero
- [ ] Implement in blog post templates
- [ ] Add to service pages
- [ ] Set up exit intent popup
- [ ] Create mobile sticky version
- [ ] Implement analytics tracking
- [ ] A/B test different messages
- [ ] Monitor conversion rates
- [ ] Optimize based on performance

This hook line implementation will significantly boost your free registration conversions by clearly communicating the value proposition and making the offer irresistible!